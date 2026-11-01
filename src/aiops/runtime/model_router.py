"""Task-tier model routing via LiteLLM; remote models are blocked by default."""
from __future__ import annotations
import os
from enum import Enum
from typing import Any

class ModelTier(str, Enum):
    FAST = "fast"
    STRONG = "strong"
    DEEP = "deep"

class ModelNotConfigured(RuntimeError):
    pass

class ModelRouter:
    def __init__(self, models: dict[str, str] | None = None, allow_remote: bool | None = None, max_tokens: int | None = None) -> None:
        self.models = models or {key: os.getenv(f"AIOPS_MODEL_{key.upper()}", "").strip() for key in ("fast","strong","deep")}
        self.allow_remote = os.getenv("AIOPS_ALLOW_REMOTE_MODELS","false").lower() == "true" if allow_remote is None else allow_remote
        self.max_tokens = max_tokens or int(os.getenv("AIOPS_MAX_TOKENS","4096"))

    def select(self, tier: ModelTier | str) -> str:
        key = tier.value if isinstance(tier, ModelTier) else str(tier)
        model = self.models.get(key, "")
        if not model: raise ModelNotConfigured(f"No model configured for tier '{key}'. Set AIOPS_MODEL_{key.upper()}.")
        remote = ("openai/","anthropic/","gemini/","azure/","bedrock/","vertex_ai/")
        if not self.allow_remote and model.startswith(remote):
            raise ModelNotConfigured("Remote model blocked; set AIOPS_ALLOW_REMOTE_MODELS=true only when charges are accepted.")
        return model

    def complete(self, messages: list[dict[str, Any]], tier: ModelTier | str = ModelTier.STRONG, max_tokens: int | None = None, **kwargs: Any) -> Any:
        model = self.select(tier)
        try: from litellm import completion
        except ImportError as exc: raise RuntimeError("Install with pip install -e '.[llm]'") from exc
        tier_key = tier.value if isinstance(tier, ModelTier) else str(tier)
        tier_cap = int(os.getenv(f"AIOPS_MAX_TOKENS_{tier_key.upper()}", str(self.max_tokens)))
        output_cap = max(1, min(max_tokens or tier_cap, tier_cap, self.max_tokens))
        return completion(model=model, messages=messages, max_tokens=output_cap, **kwargs)
