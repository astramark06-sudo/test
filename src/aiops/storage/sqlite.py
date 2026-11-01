"""SQLite run ledger, workflow checkpoints, source and memory storage."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, workflow TEXT NOT NULL, status TEXT NOT NULL, input_json TEXT NOT NULL, output_json TEXT, error TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS steps(run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE, step_name TEXT NOT NULL, status TEXT NOT NULL, input_json TEXT, output_json TEXT, error TEXT, attempts INTEGER NOT NULL DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(run_id,step_name));
CREATE TABLE IF NOT EXISTS artifacts(artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,path TEXT NOT NULL,kind TEXT,sha256 TEXT,metadata_json TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS sources(source_id INTEGER PRIMARY KEY AUTOINCREMENT,uri TEXT NOT NULL UNIQUE,title TEXT,source_type TEXT,retrieved_at TEXT,claims_json TEXT,metadata_json TEXT);
CREATE TABLE IF NOT EXISTS memories(memory_id INTEGER PRIMARY KEY AUTOINCREMENT,namespace TEXT NOT NULL,title TEXT NOT NULL,body TEXT NOT NULL,metadata_json TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS dataset_records (
  dataset TEXT NOT NULL, record_key TEXT NOT NULL, source_file TEXT,
  payload_json TEXT NOT NULL, imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(dataset, record_key)
);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status,updated_at);
CREATE INDEX IF NOT EXISTS idx_steps_status ON steps(run_id,status);
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace,updated_at);
"""

class SQLiteStore:
    def __init__(self, path: str | Path = "./data/aiops.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def initialize(self) -> None:
        with self.connect() as con:
            con.executescript(SCHEMA)
            con.execute("""CREATE TABLE IF NOT EXISTS model_usage (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, model TEXT, tier TEXT,
                prompt_tokens INTEGER, completion_tokens INTEGER, total_tokens INTEGER, cost_usd REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            try:
                con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(title,body,content='memories',content_rowid='memory_id')")
                con.executescript("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN INSERT INTO memories_fts(rowid,title,body) VALUES(new.memory_id,new.title,new.body); END;
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN INSERT INTO memories_fts(memories_fts,rowid,title,body) VALUES('delete',old.memory_id,old.title,old.body); END;
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN INSERT INTO memories_fts(memories_fts,rowid,title,body) VALUES('delete',old.memory_id,old.title,old.body); INSERT INTO memories_fts(rowid,title,body) VALUES(new.memory_id,new.title,new.body); END;
                """)
            except sqlite3.OperationalError:
                pass  # LIKE fallback remains available without FTS5.

    def create_run(self, run_id: str, workflow: str, payload: dict[str, Any]) -> None:
        with self.connect() as con:
            con.execute("INSERT OR IGNORE INTO runs(run_id,workflow,status,input_json) VALUES(?,?,?,?)", (run_id, workflow, "queued", json.dumps(payload, ensure_ascii=False)))

    def set_run_status(self, run_id: str, status: str, output: Any = None, error: str | None = None) -> None:
        with self.connect() as con:
            con.execute("UPDATE runs SET status=?,output_json=?,error=?,updated_at=CURRENT_TIMESTAMP WHERE run_id=?", (status, json.dumps(output, ensure_ascii=False) if output is not None else None, error, run_id))

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None: return None
            value = dict(row)
            value["input"] = json.loads(value.pop("input_json"))
            value["output"] = json.loads(value["output_json"]) if value["output_json"] else None
            return value

    def get_step(self, run_id: str, step_name: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM steps WHERE run_id=? AND step_name=?", (run_id, step_name)).fetchone()
            if row is None: return None
            value = dict(row)
            for col, key in (("input_json", "input"), ("output_json", "output")):
                value[key] = json.loads(value[col]) if value[col] else None
                value.pop(col)
            return value

    def save_step(self, run_id: str, step_name: str, status: str, input_data: Any = None, output: Any = None, error: str | None = None) -> None:
        with self.connect() as con:
            con.execute("""INSERT INTO steps(run_id,step_name,status,input_json,output_json,error,attempts) VALUES(?,?,?,?,?,?,CASE WHEN ?='running' THEN 1 ELSE 0 END)
            ON CONFLICT(run_id,step_name) DO UPDATE SET status=excluded.status,input_json=excluded.input_json,output_json=excluded.output_json,error=excluded.error,attempts=steps.attempts+CASE WHEN excluded.status='running' THEN 1 ELSE 0 END,updated_at=CURRENT_TIMESTAMP""",
            (run_id, step_name, status, json.dumps(input_data, ensure_ascii=False) if input_data is not None else None, json.dumps(output, ensure_ascii=False) if output is not None else None, error, status))

    def add_memory(self, namespace: str, title: str, body: str, metadata: dict[str, Any] | None = None) -> int:
        with self.connect() as con:
            cur = con.execute("INSERT INTO memories(namespace,title,body,metadata_json) VALUES(?,?,?,?)", (namespace, title, body, json.dumps(metadata or {}, ensure_ascii=False)))
            return int(cur.lastrowid)

    def search_memory(self, query: str, namespace: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        terms = [term for term in query.split() if term]
        if not terms: return []
        with self.connect() as con:
            try:
                sql = "SELECT m.* FROM memories_fts f JOIN memories m ON m.memory_id=f.rowid WHERE memories_fts MATCH ?"
                args: list[Any] = [" AND ".join('"' + term.replace('"','""') + '"' for term in terms)]
                if namespace: sql += " AND m.namespace=?"; args.append(namespace)
                sql += " ORDER BY rank LIMIT ?"; args.append(limit)
                rows = con.execute(sql,args).fetchall()
            except sqlite3.OperationalError:
                sql = "SELECT * FROM memories WHERE title LIKE ? OR body LIKE ?"
                args = [f"%{terms[0]}%",f"%{terms[0]}%"]
                if namespace: sql += " AND namespace=?"; args.append(namespace)
                sql += " ORDER BY updated_at DESC LIMIT ?"; args.append(limit)
                rows = con.execute(sql,args).fetchall()
            return [dict(row) for row in rows]

    def record_source(self, uri: str, title: str | None = None, source_type: str | None = None,
                      claims: list[str] | None = None, metadata: dict[str, Any] | None = None) -> None:
        with self.connect() as con:
            con.execute("""INSERT INTO sources(uri,title,source_type,retrieved_at,claims_json,metadata_json)
              VALUES(?,?,?,CURRENT_TIMESTAMP,?,?) ON CONFLICT(uri) DO UPDATE SET
              title=excluded.title,source_type=excluded.source_type,retrieved_at=CURRENT_TIMESTAMP,
              claims_json=excluded.claims_json,metadata_json=excluded.metadata_json""",
              (uri,title,source_type,json.dumps(claims or [],ensure_ascii=False),
               json.dumps(metadata or {},ensure_ascii=False)))

    def list_sources(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [dict(row) for row in con.execute("SELECT * FROM sources ORDER BY retrieved_at DESC LIMIT ?",(limit,)).fetchall()]

    def record_artifact(self, path: str | Path, run_id: str | None = None, kind: str | None = None,
                        sha256: str | None = None, metadata: dict[str, Any] | None = None) -> int:
        with self.connect() as con:
            cur=con.execute("INSERT INTO artifacts(run_id,path,kind,sha256,metadata_json) VALUES(?,?,?,?,?)",
              (run_id,str(path),kind,sha256,json.dumps(metadata or {},ensure_ascii=False)))
            return int(cur.lastrowid)

    def list_artifacts(self, run_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as con:
            if run_id:
                rows=con.execute("SELECT * FROM artifacts WHERE run_id=? ORDER BY created_at DESC LIMIT ?",(run_id,limit)).fetchall()
            else:
                rows=con.execute("SELECT * FROM artifacts ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
            return [dict(row) for row in rows]

    def record_model_usage(self, model: str | None, tier: str | None, prompt_tokens: int = 0,
                           completion_tokens: int = 0, total_tokens: int | None = None,
                           cost_usd: float | None = None, run_id: str | None = None) -> int:
        total = total_tokens if total_tokens is not None else prompt_tokens + completion_tokens
        with self.connect() as con:
            cur=con.execute("INSERT INTO model_usage(run_id,model,tier,prompt_tokens,completion_tokens,total_tokens,cost_usd) VALUES(?,?,?,?,?,?,?)",
              (run_id,model,tier,prompt_tokens,completion_tokens,total,cost_usd))
            return int(cur.lastrowid)

    def list_model_usage(self, run_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as con:
            if run_id:
                rows=con.execute("SELECT * FROM model_usage WHERE run_id=? ORDER BY created_at DESC LIMIT ?",(run_id,limit)).fetchall()
            else:
                rows=con.execute("SELECT * FROM model_usage ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
            return [dict(row) for row in rows]

    def usage_summary(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Aggregate observed usage and reported provider cost by model and task tier."""
        with self.connect() as con:
            sql = "SELECT model,tier,COUNT(*) AS calls,SUM(prompt_tokens) AS prompt_tokens,SUM(completion_tokens) AS completion_tokens,SUM(total_tokens) AS total_tokens,SUM(cost_usd) AS cost_usd FROM model_usage"
            args: list[Any] = []
            if run_id:
                sql += " WHERE run_id=?"
                args.append(run_id)
            sql += " GROUP BY model,tier ORDER BY total_tokens DESC"
            return [dict(row) for row in con.execute(sql, args).fetchall()]

    def import_dataset_batches(
        self,
        batches: list[dict[str, Any]],
        sources: list[dict[str, Any]] | None = None,
    ) -> dict[str, dict[str, int]]:
        """Atomically import multiple datasets and their source-index records.

        Each batch must contain dataset, rows, key_field and source_file. All
        dataset upserts and source-index updates share one SQLite transaction,
        so a failure cannot leave a partially imported bundle.
        """
        import hashlib

        imported: dict[str, int] = {}
        with self.connect() as con:
            for batch in batches:
                dataset = str(batch["dataset"])
                rows = batch["rows"]
                key_field = batch.get("key_field")
                source_file = batch.get("source_file")
                for row in rows:
                    if key_field:
                        record_key = str(row[key_field])
                    else:
                        canonical = json.dumps(
                            row, sort_keys=True, ensure_ascii=False
                        )
                        record_key = hashlib.sha256(
                            canonical.encode("utf-8")
                        ).hexdigest()
                    con.execute(
                        """INSERT INTO dataset_records(
                            dataset,record_key,source_file,payload_json
                        ) VALUES(?,?,?,?) ON CONFLICT(dataset,record_key) DO UPDATE SET
                        source_file=excluded.source_file,
                        payload_json=excluded.payload_json,
                        imported_at=CURRENT_TIMESTAMP""",
                        (
                            dataset,
                            record_key,
                            source_file,
                            json.dumps(row, ensure_ascii=False),
                        ),
                    )
                    imported[dataset] = imported.get(dataset, 0) + 1

            for source in sources or []:
                con.execute(
                    """INSERT INTO sources(
                        uri,title,source_type,retrieved_at,claims_json,metadata_json
                    ) VALUES(?,?,?,CURRENT_TIMESTAMP,?,?)
                    ON CONFLICT(uri) DO UPDATE SET
                    title=excluded.title,
                    source_type=excluded.source_type,
                    retrieved_at=CURRENT_TIMESTAMP,
                    claims_json=excluded.claims_json,
                    metadata_json=excluded.metadata_json""",
                    (
                        source["uri"],
                        source.get("title"),
                        source.get("source_type"),
                        json.dumps(source.get("claims") or [], ensure_ascii=False),
                        json.dumps(source.get("metadata") or {}, ensure_ascii=False),
                    ),
                )

            result = {}
            for dataset, rows_imported in imported.items():
                row = con.execute(
                    "SELECT COUNT(*) AS n FROM dataset_records WHERE dataset=?",
                    (dataset,),
                ).fetchone()
                result[dataset] = {
                    "rows_imported": rows_imported,
                    "stored_rows_after_import": int(row["n"]),
                }
            return result

    def upsert_dataset_records(self, dataset: str, rows: list[dict[str, Any]],
                               key_field: str | None = None, source_file: str | None = None) -> int:
        """Import structured rows while retaining the complete original row as JSON."""
        import hashlib
        count = 0
        with self.connect() as con:
            for row in rows:
                if key_field and row.get(key_field) not in (None, ""):
                    record_key = str(row[key_field])
                else:
                    canonical = json.dumps(row, sort_keys=True, ensure_ascii=False)
                    record_key = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                con.execute("""INSERT INTO dataset_records(dataset,record_key,source_file,payload_json)
                  VALUES(?,?,?,?) ON CONFLICT(dataset,record_key) DO UPDATE SET
                  source_file=excluded.source_file,payload_json=excluded.payload_json,
                  imported_at=CURRENT_TIMESTAMP""",
                  (dataset, record_key, source_file, json.dumps(row, ensure_ascii=False)))
                count += 1
        return count

    def list_dataset_records(self, dataset: str, query: str | None = None,
                              limit: int = 1000) -> list[dict[str, Any]]:
        with self.connect() as con:
            if query:
                rows = con.execute("SELECT * FROM dataset_records WHERE dataset=? AND payload_json LIKE ? ORDER BY record_key LIMIT ?",
                                   (dataset, f"%{query}%", max(1, min(limit, 100000)))).fetchall()
            else:
                rows = con.execute("SELECT * FROM dataset_records WHERE dataset=? ORDER BY record_key LIMIT ?",
                                   (dataset, max(1, min(limit, 100000)))).fetchall()
            output = []
            for row in rows:
                item = dict(row)
                item["record"] = json.loads(item.pop("payload_json"))
                output.append(item)
            return output

    def count_dataset_records(self, dataset: str) -> int:
        with self.connect() as con:
            row = con.execute("SELECT COUNT(*) AS n FROM dataset_records WHERE dataset=?", (dataset,)).fetchone()
            return int(row["n"])
