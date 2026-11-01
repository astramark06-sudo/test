"""Conservative laptop configuration matching by exact brand and CPU identity."""
from __future__ import annotations

import re
from typing import Any


_CAPACITY = re.compile(r"(?<![a-z0-9.])(\d+(?:\.\d+)?)\s*(tb|gb|mb)\b", re.I)
_CAPACITY_TO_GB = {"tb": 1000.0, "gb": 1.0, "mb": 0.001}


def normalize(value: Any) -> str:
    """Normalize text for exact brand/processor comparisons."""
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _first_capacity_gb(value: Any) -> float | None:
    """Read the first stated capacity, normally installed capacity before upgrade notes.

    Returning only the first capacity avoids mistaking an expandable maximum or
    an individual memory module for the installed total later in the same text.
    """
    match = _CAPACITY.search(str(value or ""))
    if not match:
        return None
    return float(match.group(1)) * _CAPACITY_TO_GB[match.group(2).lower()]


def _capacity_compatible(candidate: Any, researched: Any) -> bool:
    """Reject a capacity conflict, but do not treat missing evidence as a match."""
    observed = _first_capacity_gb(candidate)
    known = _first_capacity_gb(researched)
    return observed is None or known is None or observed == known


def match_configuration(
    candidate: dict[str, Any],
    configurations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Match only exact brand/CPU rows, then use capacities to reject conflicts.

    Capacity evidence can narrow a candidate set, but a unique row is never
    labelled an exact SKU match. Missing capacity evidence remains unknown.
    """
    brand = normalize(candidate.get("Brand_detected"))
    cpu = normalize(candidate.get("Processor_detected"))
    pool = [
        row
        for row in configurations
        if normalize(row.get("Brand")) == brand
        and cpu
        and normalize(row.get("Processor")) == cpu
    ]
    if not pool:
        return {"match_status": "unmatched", "match_confidence": "none"}

    ram_observed = _first_capacity_gb(candidate.get("RAM_detected"))
    storage_observed = _first_capacity_gb(candidate.get("Storage_detected"))
    observed_fields = [
        ("RAM_detected", "RAM_seen", ram_observed),
        ("Storage_detected", "Storage_seen", storage_observed),
    ]
    narrowed = [
        row
        for row in pool
        if _capacity_compatible(candidate.get("RAM_detected"), row.get("RAM_seen"))
        and _capacity_compatible(
            candidate.get("Storage_detected"), row.get("Storage_seen")
        )
    ]

    if len(narrowed) == 1:
        row = narrowed[0]
        keys = (
            "Model_family",
            "Processor",
            "RAM_seen",
            "Storage_seen",
            "OS_or_device_type",
            "Research_notes",
            "Match_confidence",
        )
        comparable = [
            field
            for field, config_field, observed in observed_fields
            if observed is not None
            and _first_capacity_gb(row.get(config_field)) is not None
        ]
        confirmed = [
            field
            for field, config_field, observed in observed_fields
            if observed is not None
            and _first_capacity_gb(row.get(config_field)) == observed
        ]
        all_observed_capacities_confirmed = (
            bool(observed_fields and any(item[2] is not None for item in observed_fields))
            and len(confirmed)
            == sum(item[2] is not None for item in observed_fields)
        )

        if all_observed_capacities_confirmed:
            status = "unique_configuration_consistent_with_observed_capacities"
            confidence = "medium"
        else:
            status = "unique_brand_cpu_family_only"
            confidence = "low" if any(item[2] is not None for item in observed_fields) else "medium"

        return {
            **{f"researched_{key}": row.get(key) for key in keys},
            "match_status": status,
            "match_confidence": confidence,
            "capacity_fields_compared": comparable,
            "capacity_fields_confirmed": confirmed,
        }

    status = (
        "ambiguous_multiple_configurations"
        if len(pool) > 1
        else "ocr_configuration_mismatch"
    )
    return {"match_status": status, "match_confidence": "low"}
