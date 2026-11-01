"""Command-line entry point."""

import argparse
import json
from pathlib import Path

from aiops.export.jsonl import write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="aiops", description="AI Operations Platform utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-jsonl", help="Check that every JSONL line is valid JSON")
    validate.add_argument("path", type=Path)
    export = sub.add_parser("export-jsonl", help="Write JSON records to JSONL")
    export.add_argument("input", type=Path, help="JSON file containing an array of objects")
    export.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.command == "validate-jsonl":
        count = 0
        with args.path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if line.strip():
                    json.loads(line)
                    count += 1
        print(f"Valid JSONL: {count} records")
    elif args.command == "export-jsonl":
        records = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
            raise SystemExit("Input must be a JSON array of objects")
        print(write_jsonl(records, args.output))


if __name__ == "__main__":
    main()
