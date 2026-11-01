"""Conservative laptop configuration matching by exact brand and CPU identity."""
import re
from typing import Any

def normalize(value: Any) -> str: return re.sub(r"[^a-z0-9]+","",str(value or "").casefold())

def match_configuration(candidate: dict[str,Any], configurations: list[dict[str,Any]]) -> dict[str,Any]:
    brand=normalize(candidate.get("Brand_detected")); cpu=normalize(candidate.get("Processor_detected"))
    pool=[row for row in configurations if normalize(row.get("Brand"))==brand and cpu and normalize(row.get("Processor"))==cpu]
    if not pool: return {"match_status":"unmatched","match_confidence":"none"}
    ram=normalize(candidate.get("RAM_detected")); storage=normalize(candidate.get("Storage_detected"))
    narrowed=[row for row in pool if (not ram or ram in normalize(row.get("RAM_seen"))) and (not storage or storage in normalize(row.get("Storage_seen")))]
    if len(narrowed)==1:
        row=narrowed[0]
        keys=("Model_family","Processor","RAM_seen","Storage_seen","OS_or_device_type","Research_notes","Match_confidence")
        status="exact_configuration" if len(pool)>1 else "exact_cpu_brand_unique_config"
        return {**{f"researched_{key}":row.get(key) for key in keys},"match_status":status,"match_confidence":"high" if len(pool)>1 else "medium"}
    if len(pool)==1 and not (ram or storage):
        row=pool[0]; keys=("Model_family","Processor","RAM_seen","Storage_seen","OS_or_device_type","Research_notes","Match_confidence")
        return {**{f"researched_{key}":row.get(key) for key in keys},"match_status":"unique_brand_cpu_family_only","match_confidence":"medium"}
    return {"match_status":"ambiguous_multiple_configurations" if len(pool)>1 else "ocr_configuration_mismatch","match_confidence":"low"}
