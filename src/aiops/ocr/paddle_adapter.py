"""PaddleOCR 3.x adapter with normalized, evidence-preserving line records."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _result_mapping(result: Any) -> Mapping[str, Any]:
    """Return the OCR result payload across PaddleOCR 3.x result wrappers."""
    if isinstance(result, Mapping):
        payload: Any = result
    else:
        payload = getattr(result, "json", None)
        if callable(payload):
            payload = payload()
    if not isinstance(payload, Mapping):
        raise TypeError(
            "PaddleOCR returned an unsupported result object; expected a mapping "
            "or an object exposing a mapping-valued .json property."
        )
    nested = payload.get("res")
    return nested if isinstance(nested, Mapping) else payload


def _to_plain_value(value: Any) -> Any:
    """Convert NumPy-like arrays/scalars to Python values without importing NumPy."""
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return tolist()
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, tuple):
        return [_to_plain_value(part) for part in value]
    if isinstance(value, list):
        return [_to_plain_value(part) for part in value]
    return value


def run_paddle_ocr(image_path: str, language: str = "en") -> list[dict[str, Any]]:
    """Run PaddleOCR 3.x and return one normalized record per recognized line.

    PaddleOCR 3.x uses `predict()` and dict-like result objects. The adapter
    retains text, per-line confidence and four-point polygon coordinates.
    Original-image coordinates are preserved by disabling page rotation and
    document unwarping; line-orientation classification remains enabled.
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError(
            "PaddleOCR is not installed. Install the optional OCR extra: "
            "pip install -e '.[ocr]'"
        ) from exc

    engine = PaddleOCR(
        lang=language,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=True,
        engine="paddle",
    )
    results = engine.predict(image_path)
    lines: list[dict[str, Any]] = []

    for page in results or []:
        payload = _result_mapping(page)
        texts = payload.get("rec_texts")
        if texts is None:
            texts = []
        scores = payload.get("rec_scores")
        polygons = payload.get("rec_polys")
        if polygons is None:
            polygons = payload.get("dt_polys")

        for index, raw_text in enumerate(texts):
            if raw_text is None:
                continue
            confidence = None
            if scores is not None and index < len(scores):
                try:
                    confidence = float(_to_plain_value(scores[index]))
                except (TypeError, ValueError):
                    confidence = None

            bbox = None
            if polygons is not None and index < len(polygons):
                bbox = _to_plain_value(polygons[index])

            lines.append(
                {
                    "text": str(raw_text),
                    "confidence": confidence,
                    "bbox": bbox,
                    "engine": "paddleocr",
                }
            )
    return lines
