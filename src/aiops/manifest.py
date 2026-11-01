"""Deterministic SHA-256 manifests for immutable source and release folders."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


CHUNK_SIZE = 1024 * 1024
SCHEMA_VERSION = 1


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _inventory(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not allowed in a release manifest: {path}")
        if not path.is_file():
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return files


def build_manifest(
    directory: str | Path,
    output: str | Path,
) -> Path:
    """Write an atomic JSON manifest; output must be outside the inventoried tree."""
    root = Path(directory).expanduser().resolve()
    destination = Path(output).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Manifest root is not a directory: {root}")
    if destination == root or root in destination.parents:
        raise ValueError("Manifest output must be outside the inventoried directory")

    files = _inventory(root)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "algorithm": "sha256",
        "files": files,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def verify_manifest(
    directory: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Verify hashes, sizes, missing files and unlisted extra files."""
    root = Path(directory).expanduser().resolve()
    manifest_file = Path(manifest_path).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Verification root is not a directory: {root}")
    if not manifest_file.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")
    if manifest_file == root or root in manifest_file.parents:
        raise ValueError("Manifest file must be outside the inventoried directory")

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read manifest {manifest_file}: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ValueError("Manifest root must be an object")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported manifest schema version")
    if manifest.get("algorithm") != "sha256":
        raise ValueError("Unsupported manifest hash algorithm")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("Manifest files must be a list")

    expected: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Every manifest entry must be an object")
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            raise ValueError("Manifest entry has an invalid path")
        pure = PurePosixPath(relative)
        if (
            pure.is_absolute()
            or "\\" in relative
            or ".." in pure.parts
            or "." in pure.parts
            or pure.as_posix() != relative
        ):
            raise ValueError(f"Unsafe manifest path: {relative!r}")
        size = entry.get("size_bytes")
        digest = entry.get("sha256")
        if type(size) is not int or size < 0:
            raise ValueError(f"Invalid file size for manifest path: {relative}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid SHA-256 value for manifest path: {relative}")
        if relative in expected:
            raise ValueError(f"Duplicate manifest path: {relative}")
        expected[relative] = entry

    actual_paths: set[str] = set()
    checked = []
    errors = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            errors.append(f"symlink not allowed: {path.relative_to(root).as_posix()}")
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        actual_paths.add(relative)
        entry = expected.get(relative)
        if entry is None:
            errors.append(f"unlisted file: {relative}")
            continue
        size = path.stat().st_size
        digest = _sha256(path)
        if size != entry.get("size_bytes"):
            errors.append(f"size mismatch: {relative}")
        if digest != entry.get("sha256"):
            errors.append(f"SHA-256 mismatch: {relative}")
        checked.append(relative)

    for missing in sorted(set(expected) - actual_paths):
        errors.append(f"missing file: {missing}")

    return {
        "valid": not errors,
        "files_expected": len(expected),
        "files_checked": len(checked),
        "errors": errors,
    }
