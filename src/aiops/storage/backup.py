"""Consistent SQLite backup utility for local research and run databases."""
from __future__ import annotations

import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


def backup_database(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Create and integrity-check a consistent online backup.

    The source is opened read-only and copied through SQLite's backup API, which
    includes committed WAL contents. The completed temporary copy replaces the
    destination atomically. A failed copy never destroys an existing destination.
    """
    source = Path(source_path).expanduser()
    destination = Path(destination_path).expanduser()

    if not source.is_file():
        raise FileNotFoundError(f"SQLite source database not found: {source}")
    if source.resolve() == destination.resolve():
        raise ValueError("Backup destination must differ from the source database")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Backup destination already exists: {destination}; "
            "pass overwrite=True to replace it"
        )
    if destination.exists() and not destination.is_file():
        raise ValueError(f"Backup destination is not a regular file: {destination}")

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(fd)
    temporary = Path(temporary_name)

    try:
        source_uri = source.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True, timeout=30)) as source_db:
            with closing(sqlite3.connect(temporary, timeout=30)) as backup_db:
                source_db.backup(backup_db)
                result = backup_db.execute("PRAGMA integrity_check").fetchone()
                if not result or result[0] != "ok":
                    detail = result[0] if result else "no result"
                    raise sqlite3.DatabaseError(
                        f"SQLite backup integrity_check failed: {detail}"
                    )
        if destination.exists() and not overwrite:
            raise FileExistsError(
                f"Backup destination appeared during backup: {destination}"
            )
        os.replace(temporary, destination)
        return destination
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
