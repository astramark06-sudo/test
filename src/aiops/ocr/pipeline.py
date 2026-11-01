"""Multi-engine OCR runner preserving every engine result and failure."""
from pathlib import Path
from typing import Any
from aiops.validation.reconcile import reconcile_text

def run_multi_engine_ocr(image_path: str | Path, engines: tuple[str,...] = ("paddleocr",)) -> dict[str,Any]:
    outputs={}; errors={}
    for name in engines:
        try:
            if name=="paddleocr":
                from aiops.ocr.paddle_adapter import run_paddle_ocr
                outputs[name]=run_paddle_ocr(str(image_path))
            elif name=="easyocr":
                from aiops.ocr.easyocr_adapter import run_easyocr
                outputs[name]=run_easyocr(str(image_path))
            elif name=="tesseract":
                from aiops.ocr.tesseract_adapter import run_tesseract
                outputs[name]=run_tesseract(str(image_path))
            else: errors[name]="Unsupported OCR engine"
        except Exception as exc: errors[name]=f"{type(exc).__name__}: {exc}"
    lines={engine:[{"text":token.get("text","")} for token in tokens] for engine,tokens in outputs.items()}
    reconciliation=reconcile_text(lines)
    return {"source_file":str(image_path),"engine_outputs":outputs,"reconciliation":reconciliation,
            "engine_errors":errors,"review_required":bool(errors) or reconciliation["review_required"]}
