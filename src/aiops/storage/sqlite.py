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
