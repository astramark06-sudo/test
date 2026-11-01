"""Record model token/cost usage in the local run ledger."""
from typing import Any
from aiops.storage.sqlite import SQLiteStore

def _get(obj: Any, name: str, default: Any = None) -> Any:
    return obj.get(name,default) if isinstance(obj,dict) else getattr(obj,name,default)

def record_response_usage(store: SQLiteStore, response: Any, tier: str, run_id: str | None = None) -> int:
    usage=_get(response,"usage",{}) or {}; hidden=_get(response,"_hidden_params",{}) or {}
    prompt=int(_get(usage,"prompt_tokens",0) or 0); completion=int(_get(usage,"completion_tokens",0) or 0)
    total=int(_get(usage,"total_tokens",prompt+completion) or prompt+completion)
    return store.record_model_usage(_get(response,"model"),tier,prompt,completion,total,_get(hidden,"response_cost"),run_id)
