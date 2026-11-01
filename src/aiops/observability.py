"""Opt-in LiteLLM -> Langfuse trace callback."""
import os

from aiops.config import load_environment

def configure_langfuse_for_litellm() -> bool:
    load_environment()
    if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")): return False
    try: import litellm
    except ImportError as exc: raise RuntimeError("Install both llm and observability extras") from exc
    callbacks=list(getattr(litellm,"success_callback",[]) or [])
    if "langfuse" not in callbacks: callbacks.append("langfuse")
    litellm.success_callback=callbacks
    return True
