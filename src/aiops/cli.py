"""Local operations command line."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from aiops.diagnostics import collect_diagnostics, diagnostics_failed, render_diagnostics
from aiops.export.jsonl import write_jsonl
from aiops.research.import_validation import load_csv_batch
from aiops.storage.sqlite import SQLiteStore


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aiops",
        description="AI Operations Platform utilities",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-jsonl", help="Validate JSON Lines")
    validate.add_argument("path", type=Path)

    export = sub.add_parser("export-jsonl", help="Export a JSON array to JSONL")
    export.add_argument("input", type=Path)
    export.add_argument("output", type=Path)

    init_db = sub.add_parser("init-db", help="Initialize local SQLite storage")
    init_db.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )

    csv_export = sub.add_parser("csv-to-jsonl", help="Convert CSV rows to JSONL")
    csv_export.add_argument("input", type=Path)
    csv_export.add_argument("output", type=Path)

    status = sub.add_parser("run-status", help="Inspect a workflow run")
    status.add_argument("run_id")
    status.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )

    usage = sub.add_parser("usage-report", help="Summarize model token usage")
    usage.add_argument("--run-id")
    usage.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )

    ingest = sub.add_parser("ingest-csv", help="Import CSV rows into local SQLite")
    ingest.add_argument("input", type=Path)
    ingest.add_argument("dataset")
    ingest.add_argument("--key-field")
    ingest.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )

    count = sub.add_parser("dataset-count", help="Count imported dataset rows")
    count.add_argument("dataset")
    count.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )

    doctor = sub.add_parser(
        "doctor",
        help="Run read-only checks for the local environment and SQLite database",
    )
    doctor.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("AIOPS_DB_PATH", "./data/aiops.db")),
    )
    doctor.add_argument("--project-root", type=Path, default=Path.cwd())
    doctor.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    args = parser.parse_args()

    if args.command == "validate-jsonl":
        count_rows = 0
        with args.path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise SystemExit(
                            f"Invalid JSON on line {line_number}: {exc}"
                        ) from exc
                    count_rows += 1
        print(f"Valid JSONL: {count_rows} records")

    elif args.command == "export-jsonl":
        rows = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise SystemExit("Input must be a JSON array of objects")
        print(write_jsonl(rows, args.output))

    elif args.command == "init-db":
        SQLiteStore(args.db)
        print(f"Initialized SQLite database: {args.db}")

    elif args.command == "csv-to-jsonl":
        rows = read_csv(args.input)
        print(write_jsonl(rows, args.output))
        print(f"Converted {len(rows)} rows")

    elif args.command == "run-status":
        record = SQLiteStore(args.db).get_run(args.run_id)
        if record is None:
            raise SystemExit(f"Run not found: {args.run_id}")
        print(json.dumps(record, indent=2, ensure_ascii=False))

    elif args.command == "usage-report":
        summary = SQLiteStore(args.db).usage_summary(args.run_id)
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    elif args.command == "ingest-csv":
        # Validate the complete CSV before constructing a database store or
        # writing any rows. This gives the generic CLI the same structural and
        # stable-key safeguards as the multi-file research-bundle importer.
        try:
            batch = load_csv_batch(args.input, args.key_field)
        except ValueError as exc:
            raise SystemExit(f"CSV preflight failed: {exc}") from exc

        store = SQLiteStore(args.db)
        imported = store.upsert_dataset_records(
            args.dataset,
            batch.rows,
            args.key_field,
            str(args.input),
        )
        print(f"Imported {imported} source rows into dataset '{args.dataset}'")
        if batch.duplicate_content_rows:
            print(
                f"Notice: {batch.duplicate_content_rows} exact duplicate-content "
                "row(s) share a deterministic hash key in this dataset."
            )

    elif args.command == "dataset-count":
        total = SQLiteStore(args.db).count_dataset_records(args.dataset)
        print(total)

    elif args.command == "doctor":
        checks = collect_diagnostics(args.db, args.project_root)
        if args.json:
            print(json.dumps(checks, indent=2, ensure_ascii=False))
        else:
            print(render_diagnostics(checks))
        if diagnostics_failed(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
