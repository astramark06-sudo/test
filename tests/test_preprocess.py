from pathlib import Path

import pytest

from aiops.ocr.preprocess import preprocess_image


def test_preprocessing_cannot_overwrite_the_source_image(tmp_path: Path):
    source = tmp_path / "original.jpg"
    original_bytes = b"original image bytes"
    source.write_bytes(original_bytes)

    with pytest.raises(ValueError, match="source images are immutable"):
        preprocess_image(source, source)

    assert source.read_bytes() == original_bytes


def test_preprocessing_rejects_a_symlink_to_the_source(tmp_path: Path):
    source = tmp_path / "original.jpg"
    alias = tmp_path / "alias.jpg"
    source.write_bytes(b"original image bytes")
    try:
        alias.symlink_to(source)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are not available on this platform")

    with pytest.raises(ValueError, match="source images are immutable"):
        preprocess_image(source, alias)

    assert source.read_bytes() == b"original image bytes"
