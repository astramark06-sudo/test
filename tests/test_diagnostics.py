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



def test_doctor_reports_host_resource_inventory_without_changing_state(
    tmp_path: Path,
):
    checks = check_map(collect_diagnostics(tmp_path / "missing.sqlite", tmp_path))

    assert checks["Host OS / architecture"]["status"] == "INFO"
    assert checks["CPU logical cores"]["status"] == "INFO"
    assert checks["Physical RAM"]["status"] == "INFO"
    assert checks["Disk free"]["status"] in {"INFO", "WARN"}
    assert checks["GPU inventory tooling"]["status"] == "INFO"



def test_doctor_accepts_all_loopback_ipv4_addresses(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.2:11434")

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)

    assert check_map(checks)["Ollama endpoint"]["status"] == "PASS"



def test_doctor_warns_for_placeholder_n8n_key_without_revealing_it(
    tmp_path: Path, monkeypatch
):
    secret = "replace-with-a-long-random-secret"
    monkeypatch.setenv("N8N_ENCRYPTION_KEY", secret)

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)
    check = check_map(checks)["n8n encryption key"]

    assert check["status"] == "WARN"
    assert secret not in repr(checks)


def test_doctor_accepts_long_n8n_key_without_revealing_it(
    tmp_path: Path, monkeypatch
):
    secret = "test-only-" + "x" * 48
    monkeypatch.setenv("N8N_ENCRYPTION_KEY", secret)

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)
    check = check_map(checks)["n8n encryption key"]

    assert check["status"] == "PASS"
    assert secret not in repr(checks)



def test_doctor_reports_all_local_inference_endpoint_states(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LM_STUDIO_BASE_URL", "http://127.0.0.4:1234")
    monkeypatch.setenv("VLLM_BASE_URL", "https://remote.example/v1")
    monkeypatch.setenv("LLAMACPP_BASE_URL", "http://[")

    checks = check_map(collect_diagnostics(tmp_path / "missing.sqlite", tmp_path))

    assert checks["LM Studio endpoint"]["status"] == "PASS"
    assert checks["vLLM endpoint"]["status"] == "WARN"
    assert checks["llama.cpp endpoint"]["status"] == "FAIL"


def test_doctor_reports_optional_package_versions_without_reading_secrets(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "never-print-this-value")

    checks = collect_diagnostics(tmp_path / "missing.sqlite", tmp_path)
    package_checks = [
        item for item in checks if item["name"].startswith("Optional:")
    ]

    assert any(item["name"] == "Optional: PaddlePaddle" for item in package_checks)
    assert all(item["status"] in {"AVAILABLE", "NOT INSTALLED"} for item in package_checks)
    assert "never-print-this-value" not in repr(checks)
