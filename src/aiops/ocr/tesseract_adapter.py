"""Optional Tesseract adapter; system Tesseract binary must be installed separately."""
from typing import Any

def run_tesseract(image_path: str, language: str = "eng", min_confidence: float = 0.0) -> list[dict[str, Any]]:
    try:
        import pytesseract
        from pytesseract import Output
    except ImportError as exc: raise RuntimeError("Install with pip install -e '.[ocr-tesseract]'") from exc
    data=pytesseract.image_to_data(image_path,lang=language,output_type=Output.DICT)
    output=[]
    for i,text in enumerate(data.get("text",[])):
        token=str(text).strip()
        try: confidence=float(data["conf"][i])
        except (TypeError,ValueError,IndexError): confidence=-1.0
        if not token or confidence<min_confidence: continue
        x,y=int(data["left"][i]),int(data["top"][i]); w,h=int(data["width"][i]),int(data["height"][i])
        output.append({"text":token,"confidence":max(0.0,confidence)/100,
                       "bbox":[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],"engine":"tesseract"})
    return output
