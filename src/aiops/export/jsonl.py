"""Auditable JSON Lines export."""
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

def write_jsonl(records: Iterable[dict[str, Any]], destination: str | Path) -> Path:
    path=Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record,ensure_ascii=False,sort_keys=True))
            stream.write(chr(10))
    return path
