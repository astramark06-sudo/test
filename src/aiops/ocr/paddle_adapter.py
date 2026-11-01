"""Lazy PaddleOCR adapter; importing the package does not install or load model weights."""

from typing import Any


def run_paddle_ocr(image_path: str, language: str = "en") -> list[dict[str, Any]]:
    """Run PaddleOCR and return normalized raw line records.

    PaddleOCR is an optional extra. Model downloads may be required on first use.
    This adapter intentionally keeps the dependency lazy so tests and exports work
    without heavyweight OCR packages installed.
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError(
            "PaddleOCR is not installed. Install the optional OCR extra: pip install -e '.[ocr]'"
        ) from exc

    engine = PaddleOCR(use_angle_cls=True, lang=language, show_log=False)
    result = engine.ocr(image_path, cls=True)
    lines: list[dict[str, Any]] = []
    for page in result or []:
        for item in page or []:
            if not item or len(item) < 2:
                continue
            box, recognition = item[0], item[1]
            text, confidence = recognition[0], recognition[1]
            lines.append({"text": text, "confidence": float(confidence), "bbox": box, "engine": "paddleocr"})
    return lines
