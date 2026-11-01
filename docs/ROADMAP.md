# Status and extension plan

## Implemented

- Local SQLite ledger for runs, step states, sources and memory.
- Resumable sequential workflow engine.
- Tier-based LiteLLM-compatible model router with remote-provider guard.
- Optional LangGraph adapter.
- MCP stdio registry and tool-calling client, with per-server enable flags.
- Conservative brand/processor/RAM/storage configuration matcher.
- JSONL and CSV-to-JSONL CLI utilities.
- Optional n8n Compose service, MCP/LiteLLM/agent configuration examples, CI and tests.

## Optional, not auto-provisioned

API keys, remote models, Ollama model downloads, MCP server packages, browser binaries, PaddleOCR weights, n8n, Langfuse and Qdrant. These require host resources, network access, credentials or explicit enablement.

## Next improvements

1. Manufacturer-site research adapters with capture of URL, date and exact SKU evidence.
2. OCR quality evaluation corpus using the screenshot archive and manually corrected spans.
3. Model/SKU matching benchmark and review queue.
4. Qdrant only when local FTS retrieval is insufficient.
5. UI dashboard only after task contracts and audit logs stabilise.
