"""Optional EasyOCR adapter; language weights download on first use."""
from typing import Any

def run_easyocr(image_path: str, languages: list[str] | None = None, gpu: bool = False) -> list[dict[str, Any]]:
    try: import easyocr
    except ImportError as exc: raise RuntimeError("Install with pip install -e '.[ocr-easyocr]'") from exc
    reader=easyocr.Reader(languages or ["en"],gpu=gpu)
    return [{"text":text,"confidence":float(confidence),"bbox":box,"engine":"easyocr"}
            for box,text,confidence in reader.readtext(image_path)]
