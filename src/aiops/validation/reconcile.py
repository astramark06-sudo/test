"""Conservative OCR reconciliation: preserve all engine readings and flag conflicts."""

from collections.abc import Mapping, Sequence
from typing import Any


def reconcile_text(engine_outputs: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    """Return per-engine text, a conservative consensus, and an explicit conflict flag.

    No engine silently wins. Consensus is emitted only when normalized readings match.
    """
    readings = {
        engine: "\n".join(str(line.get("text", "")) for line in lines).strip()
        for engine, lines in engine_outputs.items()
    }
    nonempty = {name: value for name, value in readings.items() if value}
    normalized = {" ".join(value.casefold().split()) for value in nonempty.values()}
    conflict = len(normalized) > 1
    consensus = next(iter(nonempty.values())) if len(normalized) == 1 and nonempty else None
    return {
        "engine_readings": readings,
        "consensus_text": consensus,
        "conflict": conflict,
        "review_required": conflict or not nonempty,
    }
