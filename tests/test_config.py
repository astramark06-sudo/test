from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from aiops.config import load_environment
from aiops.integrations.mcp_client import MCPRegistry
from aiops.runtime.model_router import ModelRouter
from aiops.storage.sqlite import SQLiteStore


def test_environment_loader_reads_dotenv_without_overriding_shell_values(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AIOPS_TEST_FROM_DOTENV", raising=False)
    monkeypatch.setenv("AIOPS_TEST_SHELL_VALUE", "shell-wins")
    (tmp_path / ".env").write_text(
        "AIOPS_TEST_FROM_DOTENV=loaded\nAIOPS_TEST_SHELL_VALUE=file-loses\n",
        encoding="utf-8",
    )

    assert load_environment() is True
    assert os.environ["AIOPS_TEST_FROM_DOTENV"] == "loaded"
    assert os.environ["AIOPS_TEST_SHELL_VALUE"] == "shell-wins"


def test_model_router_reads_model_configuration_from_dotenv(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AIOPS_MODEL_FAST", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        "AIOPS_MODEL_FAST=ollama_chat/qwen2.5:7b\n"
        "OLLAMA_BASE_URL=http://127.0.0.1:11434\n",
        encoding="utf-8",
    )

    router = ModelRouter(allow_remote=False)

    assert router.select("fast") == "ollama_chat/qwen2.5:7b"


def test_mcp_registry_loads_dotenv_before_resolving_secrets(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AIOPS_TEST_MCP_TOKEN", raising=False)
    (tmp_path / ".env").write_text(
        "AIOPS_TEST_MCP_TOKEN=local-secret-value\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "mcp.json"
    config_path.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")

    registry = MCPRegistry(config_path)

    assert registry.resolve_env({"TOKEN": "${AIOPS_TEST_MCP_TOKEN}"}) == {
        "TOKEN": "local-secret-value"
    }


def test_cli_loads_dotenv_before_resolving_default_database_path(
    tmp_path: Path, monkeypatch
):
    from aiops.cli import main

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AIOPS_DB_PATH", raising=False)
    database = tmp_path / "from-dotenv.sqlite"
    (tmp_path / ".env").write_text(
        f"AIOPS_DB_PATH={database}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["aiops", "init-db"])

    main()

    assert database.is_file()
    assert SQLiteStore(database).count_dataset_records("not-imported") == 0



def test_environment_loader_supports_an_explicit_environment_file(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AIOPS_ENV_FILE", raising=False)
    monkeypatch.delenv("AIOPS_TEST_CUSTOM_ENV", raising=False)
    env_path = tmp_path / "config" / "work.env"
    env_path.parent.mkdir()
    env_path.write_text("AIOPS_TEST_CUSTOM_ENV=custom-file\n", encoding="utf-8")
    monkeypatch.setenv("AIOPS_ENV_FILE", str(env_path))

    assert load_environment() is True
    assert os.environ["AIOPS_TEST_CUSTOM_ENV"] == "custom-file"
