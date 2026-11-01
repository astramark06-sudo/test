"""Read-only diagnostics for local platform setup and database health."""
from __future__ import annotations

import importlib.util
import os
import platform
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


OPTIONAL_MODULES = (
    ("LiteLLM", "litellm", "llm"),
    ("LangGraph", "langgraph", "agents"),
    ("MCP SDK", "mcp", "mcp"),
    ("Playwright", "playwright", "browser"),
    ("DuckDB", "duckdb", "data"),
    ("RapidFuzz", "rapidfuzz", "data"),
    ("PaddleOCR", "paddleocr", "ocr"),
    ("OpenCV", "cv2", "ocr"),
    ("EasyOCR", "easyocr", "ocr-easyocr"),
    ("Tesseract Python wrapper", "pytesseract", "ocr-tesseract"),
    ("Langfuse", "langfuse", "observability"),
)

PROJECT_FILES = (
    ".env.example",
    ".gitignore",
    "configs/default.yaml",
    "configs/agents.yaml",
    "configs/mcp_servers.example.json",
)


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def collect_diagnostics(
    db_path: str | Path = "./data/aiops.db",
    project_root: str | Path = ".",
) -> list[dict[str, str]]:
    """Collect local environment facts without network calls or writes.

    The optional integration checks only inspect whether Python modules can be
    found. Database health uses SQLite read-only mode. Environment variable
    values, credentials and .env contents are never returned.
    """
    checks: list[dict[str, str]] = []
    version = sys.version_info
    version_text = platform.python_version()
    if version >= (3, 10):
        checks.append(_check("Python", "PASS", f"{version_text}; minimum is 3.10"))
    else:
        checks.append(_check("Python", "FAIL", f"{version_text}; minimum is 3.10"))

    sqlite_version = sqlite3.sqlite_version
    try:
        with sqlite3.connect(":memory:") as connection:
            fts5_available = connection.execute(
                "SELECT sqlite_compileoption_used('ENABLE_FTS5')"
            ).fetchone()[0] == 1
            if not fts5_available:
                connection.execute("CREATE VIRTUAL TABLE doctor_fts USING fts5(value)")
                fts5_available = True
        checks.append(
            _check(
                "SQLite",
                "PASS",
                f"{sqlite_version}; FTS5 {'available' if fts5_available else 'not available'}",
            )
        )
    except sqlite3.Error as exc:
        checks.append(_check("SQLite", "WARN", f"{sqlite_version}; FTS5 check failed: {exc}"))

    root = Path(project_root).expanduser()
    if not root.exists():
        checks.append(_check("Project root", "WARN", f"Directory not found: {root}"))
    elif not root.is_dir():
        checks.append(_check("Project root", "FAIL", f"Not a directory: {root}"))
    else:
        checks.append(_check("Project root", "PASS", str(root.resolve())))
        for relative in PROJECT_FILES:
            path = root / relative
            if path.is_file():
                checks.append(_check(f"Project file: {relative}", "PASS", "present"))
            else:
                checks.append(
                    _check(f"Project file: {relative}", "INFO", "not found from this working directory")
                )

    for label, module, extra in OPTIONAL_MODULES:
        try:
            available = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            available = False
        checks.append(
            _check(
                f"Optional: {label}",
                "AVAILABLE" if available else "NOT INSTALLED",
                f"Install with: pip install -e '.[{extra}]'" if not available else "module is discoverable",
            )
        )

    remote_flag = os.getenv("AIOPS_ALLOW_REMOTE_MODELS", "").strip().lower()
    if remote_flag in {"1", "true", "yes", "on"}:
        checks.append(
            _check(
                "Remote model access",
                "WARN",
                "explicit opt-in is enabled; review provider credentials, terms and possible charges",
            )
        )
    else:
        checks.append(
            _check(
                "Remote model access",
                "PASS",
                "not explicitly enabled; default local-only guard remains in effect",
            )
        )

    ollama_url = os.getenv("OLLAMA_BASE_URL", "").strip()
    if not ollama_url:
        checks.append(_check("Ollama endpoint", "INFO", "not configured; local inference is optional"))
    else:
        parsed = urlparse(ollama_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            checks.append(_check("Ollama endpoint", "FAIL", "configured URL is malformed"))
        elif parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
            checks.append(_check("Ollama endpoint", "PASS", "configured loopback endpoint; no connection attempted"))
        else:
            checks.append(
                _check(
                    "Ollama endpoint",
                    "WARN",
                    "non-loopback host configured; local-only routing should reject remote endpoints",
                )
            )

    database = Path(db_path).expanduser()
    if not database.exists():
        checks.append(_check("SQLite database", "INFO", f"not initialized: {database}"))
    elif not database.is_file():
        checks.append(_check("SQLite database", "FAIL", f"not a regular file: {database}"))
    else:
        try:
            uri = database.resolve().as_uri() + "?mode=ro"
            with sqlite3.connect(uri, uri=True) as connection:
                result = connection.execute("PRAGMA quick_check").fetchone()
            if result and result[0] == "ok":
                checks.append(_check("SQLite database", "PASS", f"quick_check ok: {database}"))
            else:
                detail = str(result[0] if result else "no result")
                checks.append(_check("SQLite database", "FAIL", f"quick_check: {detail}"))
        except (OSError, sqlite3.Error, ValueError) as exc:
            checks.append(_check("SQLite database", "FAIL", f"read-only integrity check failed: {exc}"))

    return checks


def diagnostics_failed(checks: list[dict[str, str]]) -> bool:
    """Return True only for failed core/runtime checks."""
    return any(item["status"] == "FAIL" for item in checks)


def render_diagnostics(checks: list[dict[str, str]]) -> str:
    """Render checks as a compact terminal report."""
    width = max((len(item["status"]) for item in checks), default=4)
    return "\n".join(
        f"{item['status']:<{width}}  {item['name']}: {item['detail']}"
        for item in checks
    )
