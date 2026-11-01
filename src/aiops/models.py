"""Core data contracts. Raw OCR evidence is retained independently of normalized fields."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class OCRToken:
    text: str
    confidence: float | None = None
    bbox: list[list[float]] | None = None
    engine: str = "unknown"


@dataclass
class OCRDocument:
    source_file: str
    page_number: int | None = None
    engine_outputs: dict[str, list[OCRToken]] = field(default_factory=dict)
    raw_text: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LaptopRecord:
    source_file: str
    raw_ocr_text: str
    brand: str | None = None
    model: str | None = None
    processor: str | None = None
    ram: str | None = None
    storage: str | None = None
    display: str | None = None
    graphics: str | None = None
    ocr_price: str | None = None
    researched_price: str | None = None
    research_source: str | None = None
    review_required: bool = False
    review_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
