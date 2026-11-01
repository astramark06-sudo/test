from __future__ import annotations

import sys
from types import ModuleType

from aiops.ocr.paddle_adapter import run_paddle_ocr


class ArrayLike:
    def __init__(self, values):
        self.values = values

    def tolist(self):
        return self.values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]


def test_paddleocr_37_adapter_normalizes_text_scores_and_polygons(monkeypatch):
    calls = {}

    class FakePaddleOCR:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def predict(self, image_path):
            calls["image_path"] = image_path
            return [{
                "res": {
                    "rec_texts": ["HP 15 Laptop", "Core i5-1335U"],
                    "rec_scores": ArrayLike([0.987, 0.954]),
                    "rec_polys": ArrayLike([
                        [[1, 2], [30, 2], [30, 12], [1, 12]],
                        [[2, 20], [40, 20], [40, 30], [2, 30]],
                    ]),
                }
            }]

    fake_module = ModuleType("paddleocr")
    fake_module.PaddleOCR = FakePaddleOCR
    monkeypatch.setitem(sys.modules, "paddleocr", fake_module)

    lines = run_paddle_ocr("source.png", language="en")

    assert calls["image_path"] == "source.png"
    assert calls["init"] == {
        "lang": "en",
        "use_doc_orientation_classify": False,
        "use_doc_unwarping": False,
        "use_textline_orientation": True,
        "engine": "paddle",
    }
    assert lines == [
        {
            "text": "HP 15 Laptop",
            "confidence": 0.987,
            "bbox": [[1, 2], [30, 2], [30, 12], [1, 12]],
            "engine": "paddleocr",
        },
        {
            "text": "Core i5-1335U",
            "confidence": 0.954,
            "bbox": [[2, 20], [40, 20], [40, 30], [2, 30]],
            "engine": "paddleocr",
        },
    ]


def test_paddleocr_adapter_accepts_dict_like_result_object(monkeypatch):
    class FakeResult(dict):
        @property
        def json(self):
            return {"rec_texts": ["₹42,990"], "rec_scores": [0.91], "rec_polys": []}

    class FakePaddleOCR:
        def __init__(self, **kwargs):
            pass

        def predict(self, image_path):
            return [FakeResult()]

    fake_module = ModuleType("paddleocr")
    fake_module.PaddleOCR = FakePaddleOCR
    monkeypatch.setitem(sys.modules, "paddleocr", fake_module)

    lines = run_paddle_ocr("price.png")

    assert lines == [
        {
            "text": "₹42,990",
            "confidence": 0.91,
            "bbox": None,
            "engine": "paddleocr",
        }
    ]


def test_paddleocr_adapter_keeps_lines_when_score_or_polygon_is_missing(monkeypatch):
    class FakePaddleOCR:
        def __init__(self, **kwargs):
            pass

        def predict(self, image_path):
            return [{"rec_texts": ["Acer Aspire 3", "8GB RAM"]}]

    fake_module = ModuleType("paddleocr")
    fake_module.PaddleOCR = FakePaddleOCR
    monkeypatch.setitem(sys.modules, "paddleocr", fake_module)

    lines = run_paddle_ocr("listing.png")

    assert [line["text"] for line in lines] == ["Acer Aspire 3", "8GB RAM"]
    assert all(line["confidence"] is None and line["bbox"] is None for line in lines)
