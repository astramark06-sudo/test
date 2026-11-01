"""Task-tier model routing via LiteLLM with local-only safety defaults."""
from __future__ import annotations

import ipaddress
import os
from enum import Enum
from typing import Any

from aiops.config import load_environment
from urllib.parse import urlparse


class ModelTier(str, Enum):
    FAST = "fast"
    STRONG = "strong"
    DEEP = "deep"


class ModelNotConfigured(RuntimeError):
    """Raised when a model is missing or violates configured routing policy."""


# Non-Ollama local backends require an explicit endpoint. This prevents a
# provider's implicit/default URL from bypassing the local-only policy.
_LOCAL_BACKENDS = {
    "ollama/": ("OLLAMA_BASE_URL", "http://localhost:11434"),
    "ollama_chat/": ("OLLAMA_BASE_URL", "http://localhost:11434"),
    "lm_studio/": ("LM_STUDIO_BASE_URL", None),
    "vllm/": ("VLLM_BASE_URL", None),
    "custom_openai/": ("CUSTOM_OPENAI_BASE_URL", None),
}
LOCAL_MODEL_PREFIXES = tuple(_LOCAL_BACKENDS)


def _is_loopback_endpoint(value: Any) -> bool:
    """Return True only for an explicit HTTP(S) URL with a loopback host."""
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    host = parsed.hostname.casefold().rstrip(".")
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class ModelRouter:
    def __init__(
        self,
        models: dict[str, str] | None = None,
        allow_remote: bool | None = None,
        max_tokens: int | None = None,
    ) -> None:
        load_environment()
        configured = {
            key: os.getenv(f"AIOPS_MODEL_{key.upper()}", "").strip()
            for key in ("fast", "strong", "deep")
        }
        self.models = models if models is not None else configured
        self.allow_remote = (
            os.getenv("AIOPS_ALLOW_REMOTE_MODELS", "false").lower() == "true"
            if allow_remote is None
            else bool(allow_remote)
        )
        self.max_tokens = max_tokens or int(os.getenv("AIOPS_MAX_TOKENS", "4096"))

    def select(self, tier: ModelTier | str) -> str:
        key = tier.value if isinstance(tier, ModelTier) else str(tier)
        model = self.models.get(key, "").strip()
        if not model:
            raise ModelNotConfigured(
                f"No model configured for tier '{key}'. Set AIOPS_MODEL_{key.upper()}."
            )

        if not self.allow_remote:
            backend = next(
                (
                    (prefix, endpoint_env, default)
                    for prefix, (endpoint_env, default) in _LOCAL_BACKENDS.items()
                    if model.startswith(prefix)
                ),
                None,
            )
            if backend is None:
                raise ModelNotConfigured(
                    "Only approved local model backends are allowed. "
                    "Set AIOPS_ALLOW_REMOTE_MODELS=true only when provider charges "
                    "and data handling are explicitly accepted."
                )

            prefix, endpoint_env, default = backend
            endpoint = os.getenv(endpoint_env, default or "").strip()
            if not endpoint:
                raise ModelNotConfigured(
                    f"Local backend '{prefix}' requires {endpoint_env} to be set "
                    "to a loopback URL."
                )
            if not _is_loopback_endpoint(endpoint):
                raise ModelNotConfigured(
                    f"Non-loopback {endpoint_env} endpoint blocked in local-only mode."
                )
        return model

    def complete(
        self,
        messages: list[dict[str, Any]],
        tier: ModelTier | str = ModelTier.STRONG,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> Any:
        model = self.select(tier)
        if not self.allow_remote:
            for endpoint_key in ("api_base", "base_url"):
                endpoint = kwargs.get(endpoint_key)
                if endpoint is not None and not _is_loopback_endpoint(endpoint):
                    raise ModelNotConfigured(
                        f"Non-loopback {endpoint_key} override blocked in local-only mode."
                    )

            if kwargs.get("api_base") is None and kwargs.get("base_url") is None:
                backend = next(
                    (
                        (endpoint_env, default)
                        for prefix, (endpoint_env, default) in _LOCAL_BACKENDS.items()
                        if model.startswith(prefix)
                    ),
                    None,
                )
                if backend is not None:
                    endpoint_env, default = backend
                    endpoint = os.getenv(endpoint_env, default or "").strip()
                    if endpoint:
                        kwargs["api_base"] = endpoint

        try:
            from litellm import completion
        except ImportError as exc:
            raise RuntimeError("Install with pip install -e '.[llm]'") from exc

        tier_key = tier.value if isinstance(tier, ModelTier) else str(tier)
        tier_cap = int(
            os.getenv(f"AIOPS_MAX_TOKENS_{tier_key.upper()}", str(self.max_tokens))
        )
        output_cap = max(1, min(max_tokens or tier_cap, tier_cap, self.max_tokens))
        return completion(
            model=model,
            messages=messages,
            max_tokens=output_cap,
            **kwargs,
        )
