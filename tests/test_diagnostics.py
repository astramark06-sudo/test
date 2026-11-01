import json
import sys
from pathlib import Path

from aiops.cli import main
from aiops.diagnostics import collect_diagnostics, diagnostics_failed
from aiops.storage.sqlite import SQLiteStore


def check_map(checks):
    return {item["name"]: item for item in checks}


def test_doctor_reports_missing_database_without_creating_it(tmp_path: Path):
    database = tmp_path / "not-created.sqlite"

    checks = collect_diagnostics(database, tmp_path)

    assert check_map(checks)["SQLite database"]["status"] == "INFO"
    assert not database.exists()
    assert not diagnostics_failed(checks)


def test_doctor_checks_existing_database_read_only(tmp_path: Path):
    database = tmp_path / "workbench.sqlite"
    SQLiteStore(database)
    original_size = database.stat().st_size

    checks = collect_diagnostics(database, tmp_path)

    assert check_map(checks)["SQLite database"]["status"] == "PASS"
    assert database.stat().st_size == original_size
    assert not diagnostics_failed(checks)


def test_doctor_flags_corrupt_database(tmp_path: Path):
    database = tmp_path / "corrupt.sqlite"
    database.write_bytes(b"not a sqlite database")

    checks = collect_diagnostics(database, tmp_path)

    assert check_map(checks)["SQLite database"]["status"] == "FAIL"
    assert diagnostics_failed(checks)


def test_doctor_warns_for_remote_model_opt_in_without_exposing_secrets(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("AIOPS_ALLOW_REMOTE_MODELS", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "never-print-this-secret")

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)

    assert check_map(checks)["Remote model access"]["status"] == "WARN"
    assert "never-print-this-secret" not in repr(checks)


def test_doctor_flags_non_loopback_ollama_endpoint(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://remote.example:11434")

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)

    assert check_map(checks)["Ollama endpoint"]["status"] == "WARN"


def test_doctor_accepts_loopback_ollama_endpoint_without_network_call(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)

    assert check_map(checks)["Ollama endpoint"]["status"] == "PASS"


def test_doctor_cli_json_output(tmp_path: Path, monkeypatch, capsys):
    database = tmp_path / "missing.sqlite"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aiops",
            "doctor",
            "--db",
            str(database),
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert isinstance(output, list)
    assert any(item["name"] == "Python" for item in output)
    assert any(item["name"] == "SQLite database" for item in output)
    assert not database.exists()
