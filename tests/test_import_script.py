import json
import subprocess
import sys
from pathlib import Path


def test_bundle_import_dry_run_does_not_create_database(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "ocr_candidate_register.csv").write_text(
        "Candidate_ID,OCR_title\nS1-001,Samsung Galaxy Book4\n",
        encoding="utf-8",
    )
    (input_dir / "ocr_candidate_register_enriched_tokens.csv").write_text(
        "Candidate_ID,OCR_title,Price_tokens\nS1-001,Samsung Galaxy Book4,\n",
        encoding="utf-8",
    )
    database = tmp_path / "must_not_exist.sqlite"
    repository_root = Path(__file__).resolve().parents[1]
    script = repository_root / "scripts" / "ingest_research_bundle.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            str(input_dir),
            "--db",
            str(database),
            "--dry-run",
        ],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    candidate_files = [
        item for item in report["files"]
        if item["dataset"] == "laptop_candidates"
    ]
    assert len(candidate_files) == 2
    assert all(item["status"] == "preflight_ok" for item in candidate_files)
    assert report["datasets"]["laptop_candidates"]["status"] == "preflight_ok"
    assert report["datasets"]["laptop_candidates"]["rows_preflighted"] == 2
    assert database.exists() is False
