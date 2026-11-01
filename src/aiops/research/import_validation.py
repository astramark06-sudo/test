"""Strict CSV preflight for repeatable research-bundle imports."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CSVBatch:
    """Validated CSV header and rows, retaining all original cell strings."""

    fieldnames: tuple[str, ...]
    rows: list[dict[str, str]]
    duplicate_content_rows: int


def load_csv_batch(path: str | Path, key_field: str | None = None) -> CSVBatch:
    """Load a UTF-8 CSV and reject structural errors before any database writes.

    Stable-key datasets reject missing, whitespace-padded and duplicate keys.
    Keyless datasets report exact duplicate rows because their importer key is
    a canonical JSON hash; those duplicates would otherwise collapse silently.
    """
    source = Path(path)
    try:
        with source.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError(f"{source}: CSV has no header row")
            if any(name is None or not name.strip() for name in fieldnames):
                raise ValueError(f"{source}: CSV contains an empty column name")
            duplicates = [
                name for name, count in Counter(fieldnames).items() if count > 1
            ]
            if duplicates:
                raise ValueError(
                    f"{source}: duplicate column names: {', '.join(duplicates)}"
                )
            if key_field and key_field not in fieldnames:
                raise ValueError(
                    f"{source}: required key column {key_field!r} is missing; "
                    f"available columns: {', '.join(fieldnames)}"
                )

            rows: list[dict[str, str]] = []
            seen_keys: set[str] = set()
            content_hashes: Counter[str] = Counter()
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"{source}: row {row_number} has more cells than the header"
                    )
                missing_cells = [
                    name for name, value in row.items() if value is None
                ]
                if missing_cells:
                    raise ValueError(
                        f"{source}: row {row_number} is shorter than the header; "
                        f"missing cells for: {', '.join(missing_cells)}"
                    )
                if key_field:
                    key = row.get(key_field, "")
                    if not key or not key.strip():
                        raise ValueError(
                            f"{source}: row {row_number} has a blank {key_field!r}"
                        )
                    if key != key.strip():
                        raise ValueError(
                            f"{source}: row {row_number} has whitespace around "
                            f"{key_field!r}: {key!r}"
                        )
                    if key in seen_keys:
                        raise ValueError(
                            f"{source}: duplicate {key_field!r} value {key!r} "
                            f"at row {row_number}"
                        )
                    seen_keys.add(key)

                canonical = json.dumps(
                    row, sort_keys=True, ensure_ascii=False, separators=(",", ":")
                )
                content_hashes[hashlib.sha256(canonical.encode("utf-8")).hexdigest()] += 1
                rows.append(dict(row))

    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError(f"Could not read CSV {source}: {exc}") from exc

    duplicate_content_rows = sum(count - 1 for count in content_hashes.values())
    return CSVBatch(tuple(fieldnames), rows, duplicate_content_rows)
