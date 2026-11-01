"""Restricted DuckDB query adapter for local CSV analytics."""
from pathlib import Path
from typing import Any

def query_file(path: str | Path, sql: str, limit: int = 1000) -> list[dict[str,Any]]:
    statement=sql.strip().rstrip(";")
    if not (statement.lower().startswith("select ") or statement.lower().startswith("with ")):
        raise ValueError("Only SELECT/WITH queries are allowed")
    if ";" in statement: raise ValueError("Only one SQL statement is allowed")
    try: import duckdb
    except ImportError as exc: raise RuntimeError("Install with pip install -e '.[data]'") from exc
    file_path=str(Path(path).resolve()).replace("'","''")
    max_rows=max(1,min(int(limit),100000))
    con=duckdb.connect(database=":memory:")
    try:
        con.execute(f"CREATE VIEW input_data AS SELECT * FROM read_csv_auto('{file_path}',header=true)")
        cursor=con.execute(f"SELECT * FROM ({statement}) AS result_rows LIMIT {max_rows}")
        names=[col[0] for col in cursor.description]
        return [dict(zip(names,row)) for row in cursor.fetchall()]
    finally: con.close()
