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

## Laptop research baseline

A private, audited dataset delivery already exists in the user's Library. The 12-tab workbook and read-only SQLite workbench should be treated as the baseline release; subsequent work should produce a versioned additive update rather than another first-pass workbook.

- 348 raw OCR candidate IDs; 220 detailed listing records.
- 215 conservative candidate-to-listing links; 133 unmatched candidates; five unpaired detailed listings.
- 195 OCR-observed price values retained separately from researched prices.
- 89 configuration rows, 39 CPU benchmark rows, 27 source references.
- 80 independently audited OCR tiles; one clipped-tail coverage gap remains unresolved.
- The latest official-source review documents model/variant conflicts and secondary-only leads. It does not silently assign exact SKUs or new retail prices.

Operational documentation:
- [Laptop dataset runbook](LAPTOP_DATASET_RUNBOOK.md)
- [Research fact schema](RESEARCH_FACT_SCHEMA.md)
- [Official model source audit](OFFICIAL_MODEL_SOURCE_AUDIT_2026-11-02.md)
- [Local deployment preflight](LOCAL_DEPLOYMENT_PREFLIGHT.md)
- [Next analysis session checklist](NEXT_ANALYSIS_SESSION_CHECKLIST.md)

## Next improvements

1. Manufacturer-site research adapters with capture of URL, date and exact SKU evidence.
2. OCR quality evaluation corpus using the screenshot archive and manually corrected spans.
3. Model/SKU matching benchmark and review queue.
4. Qdrant only when local FTS retrieval is insufficient.
5. UI dashboard only after task contracts and audit logs stabilise.
