"""Read-only diagnostics for local platform setup and database health."""
from __future__ import annotations

import importlib.util
import ipaddress
import os
import platform
import shutil
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse


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


def _total_memory_bytes() -> int | None:
    """Return physical RAM using only read-only OS APIs where available."""
    if os.name == "nt":
        try:
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatus()
            status.dwLength = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.ullTotalPhys)
        except (AttributeError, OSError, TypeError, ValueError):
            return None

    if hasattr(os, "sysconf"):
        try:
            pages = int(os.sysconf("SC_PHYS_PAGES"))
            page_size = int(os.sysconf("SC_PAGE_SIZE"))
            if pages > 0 and page_size > 0:
                return pages * page_size
        except (OSError, TypeError, ValueError):
            return None
    return None


def _human_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def _is_loopback_host(host: str) -> bool:
    """Recognize localhost and every IPv4/IPv6 loopback address."""
    normalized = host.casefold().rstrip(".")
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


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
    checks.append(
        _check(
            "Host OS / architecture",
            "INFO",
            f"{platform.system()} {platform.release()} / {platform.machine()}",
        )
    )
    checks.append(
        _check(
            "CPU logical cores",
            "INFO",
            str(os.cpu_count() or "unknown"),
        )
    )
    total_memory = _total_memory_bytes()
    checks.append(
        _check(
            "Physical RAM",
            "INFO",
            _human_bytes(total_memory) if total_memory else "unable to determine using standard OS APIs",
        )
    )
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

    disk_target = root
    while not disk_target.exists() and disk_target != disk_target.parent:
        disk_target = disk_target.parent
    try:
        disk_free = shutil.disk_usage(disk_target).free
        checks.append(_check("Disk free", "INFO", f"{_human_bytes(disk_free)} on {disk_target.resolve()}"))
    except OSError as exc:
        checks.append(_check("Disk free", "WARN", f"unable to inspect filesystem: {exc}"))

    gpu_tools = [
        name for name in ("nvidia-smi", "rocm-smi", "system_profiler", "lspci")
        if shutil.which(name)
    ]
    if gpu_tools:
        checks.append(
            _check(
                "GPU inventory tooling",
                "INFO",
                f"available command(s): {', '.join(gpu_tools)}; commands are not executed by doctor",
            )
        )
    else:
        checks.append(
            _check(
                "GPU inventory tooling",
                "INFO",
                "no standard GPU inventory command found; use the host OS device manager for GPU/VRAM details",
            )
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
        elif _is_loopback_host(parsed.hostname):
            checks.append(_check("Ollama endpoint", "PASS", "configured loopback endpoint; no connection attempted"))
        else:
            checks.append(
                _check(
                    "Ollama endpoint",
                    "WARN",
                    "non-loopback host configured; local-only routing should reject remote endpoints",
                )
            )

    n8n_key = os.getenv("N8N_ENCRYPTION_KEY", "")
    if not n8n_key:
        checks.append(
            _check("n8n encryption key", "INFO", "not configured; optional n8n service is not enabled")
        )
    elif n8n_key.casefold().startswith("replace-with") or len(n8n_key) < 32:
        checks.append(
            _check(
                "n8n encryption key",
                "WARN",
                "value appears to be a placeholder or shorter than 32 characters; replace it before n8n startup",
            )
        )
    else:
        checks.append(
            _check("n8n encryption key", "PASS", "configured with at least 32 characters; entropy is not assessed and the value is hidden")
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
