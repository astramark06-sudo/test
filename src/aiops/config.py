"""Load project environment settings without overriding explicit shell values."""
from __future__ import annotations

import os
from pathlib import Path


def load_environment(env_file: str | Path | None = None) -> bool:
    """Load a local .env file with shell variables taking precedence.

    The default file is .env in the current working directory. A custom path can
    be passed directly or selected with AIOPS_ENV_FILE. Secret values are never
    logged or returned.
    """
    from dotenv import load_dotenv

    configured = env_file or os.getenv("AIOPS_ENV_FILE") or ".env"
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        return False
    return load_dotenv(dotenv_path=path, override=False)
