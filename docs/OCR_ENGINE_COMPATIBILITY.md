# OCR Engine Compatibility

Last reviewed: 2026-11-02

## PaddleOCR compatibility decision

The project uses the PaddleOCR 3.x API, not the legacy 2.x interface.

- **paddleocr>=3.7,<3.8** selects the current 3.7 release line observed on PyPI at review time. The upper bound prevents a future minor API change from silently entering this adapter.
- **paddlepaddle>=3.2,<4** supplies the Paddle inference runtime. PaddleOCR's current quick start demonstrates PaddlePaddle 3.2.0 for CPU inference and states that PaddleOCR 3.x requires PaddlePaddle 3.0 or newer.
- **opencv-python-headless>=4.9** supports image preprocessing without GUI dependencies.

The adapter deliberately uses PaddleOCR with engine="paddle" and calls predict(image_path). PaddleOCR 3.x result objects are dict-like; the adapter extracts rec_texts, rec_scores and rec_polys and converts NumPy-like values to ordinary Python values. Missing scores or polygons remain null; they are not fabricated.

Document orientation classification and document unwarping are disabled so reported polygons remain associated with original-image coordinates. Text-line orientation classification is enabled to retain the old adapter's angle-correction behavior as closely as the new API permits.

## CPU and GPU installation

The OCR extra is the CPU-oriented default:

    python -m pip install -e ".[ocr]"

Do not install a GPU runtime automatically. PaddlePaddle GPU wheels must match the host operating system, Python version, CUDA version and supported GPU. Use the official PaddlePaddle installation matrix for the exact host before replacing the CPU runtime.

## OCR engines are lazy and optional

Importing the platform does not import PaddleOCR or download model weights. The PaddleOCR package and inference models are loaded only when run_paddle_ocr() is called. A first run may download inference models; do that only after checking disk space, RAM and network policy on the target host.

CI tests the adapter with mocked PaddleOCR result objects. This validates our result normalization and API call contract without downloading heavyweight inference packages or model weights. A real-image OCR smoke test remains a host deployment check and must record engine/package versions, device, model identifiers and source-image hash.

## Other OCR adapters

- Tesseract uses the separate Python wrapper extra .[ocr-tesseract] and requires the Tesseract executable to be installed separately.
- EasyOCR uses the separate extra .[ocr-easyocr]; its model weights may download on first use.
- Multi-engine runs preserve every engine's output and error. A disagreement or failed engine requires review; no OCR engine silently overrides another.

## Official references

- PaddleOCR 3.x migration notes: https://www.paddleocr.ai/main/en/update/upgrade_notes.html
- PaddleOCR Quick Start and CPU inference installation: https://www.paddleocr.ai/main/en/quick_start.html
- PaddleOCR package and release history: https://pypi.org/project/paddleocr/
- PaddlePaddle installation matrix: https://www.paddlepaddle.org.cn/en/install/quick

The PaddleOCR 2.x to 3.x upgrade is explicitly non-backward-compatible; the legacy ocr(..., cls=True) call and 2.x nested result parsing must not be reintroduced into this 3.x adapter.
