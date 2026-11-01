from __future__ import annotations

import json
from pathlib import Path

import pytest

from aiops.manifest import build_manifest, verify_manifest


def test_manifest_builds_and_verifies_a_folder(tmp_path: Path):
    source = tmp_path / "evidence"
    (source / "screenshots").mkdir(parents=True)
    (source / "screenshots" / "one.jpg").write_bytes(b"image-one")
    (source / "prices.csv").write_text("title,price\nLaptop,42990\n", encoding="utf-8")
    output = tmp_path / "evidence.sha256.json"

    assert build_manifest(source, output) == output

    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["algorithm"] == "sha256"
    assert [entry["path"] for entry in manifest["files"]] == [
        "prices.csv",
        "screenshots/one.jpg",
    ]
    report = verify_manifest(source, output)
    assert report == {
        "valid": True,
        "files_expected": 2,
        "files_checked": 2,
        "errors": [],
    }


def test_manifest_detects_tampering_missing_and_unlisted_files(tmp_path: Path):
    source = tmp_path / "release"
    source.mkdir()
    (source / "workbook.bin").write_bytes(b"baseline")
    output = tmp_path / "release.manifest.json"
    build_manifest(source, output)

    (source / "workbook.bin").write_bytes(b"modified")
    (source / "extra.txt").write_text("new file", encoding="utf-8")
    report = verify_manifest(source, output)

    assert not report["valid"]
    assert any("SHA-256 mismatch: workbook.bin" in item for item in report["errors"])
    assert "unlisted file: extra.txt" in report["errors"]


def test_manifest_detects_missing_files(tmp_path: Path):
    source = tmp_path / "evidence"
    source.mkdir()
    (source / "screenshot.jpg").write_bytes(b"original")
    output = tmp_path / "manifest.json"
    build_manifest(source, output)
    (source / "screenshot.jpg").unlink()

    report = verify_manifest(source, output)

    assert not report["valid"]
    assert "missing file: screenshot.jpg" in report["errors"]


def test_manifest_refuses_output_inside_inventoried_directory(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()

    with pytest.raises(ValueError, match="outside"):
        build_manifest(source, source / "manifest.json")


def test_manifest_refuses_symbolic_links(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target.txt"
    target.write_text("outside data", encoding="utf-8")
    link = source / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are not available on this platform")

    with pytest.raises(ValueError, match="Symbolic links"):
        build_manifest(source, tmp_path / "manifest.json")


def test_verifier_rejects_path_traversal_in_manifest(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({
            "schema_version": 1,
            "algorithm": "sha256",
            "files": [{
                "path": "../secret.txt",
                "size_bytes": 1,
                "sha256": "0" * 64,
            }],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsafe manifest path"):
        verify_manifest(source, manifest)


def test_manifest_cli_creates_and_verifies_sha256_inventory(tmp_path: Path, monkeypatch, capsys):
    import sys

    from aiops.cli import main

    source = tmp_path / "bundle"
    source.mkdir()
    (source / "source.csv").write_text("id\n1\n", encoding="utf-8")
    manifest = tmp_path / "bundle.manifest.json"

    monkeypatch.setattr(
        sys,
        "argv",
        ["aiops", "hash-tree", str(source), str(manifest)],
    )
    main()
    assert manifest.is_file()

    monkeypatch.setattr(
        sys,
        "argv",
        ["aiops", "verify-manifest", str(source), str(manifest)],
    )
    main()
    report = json.loads(capsys.readouterr().out)
    assert report["valid"] is True
