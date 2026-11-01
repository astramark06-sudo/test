# Architecture

| Layer | Default | Optional | Purpose |
|---|---|---|---|
| Orchestration | SQLite-backed workflow engine | LangGraph | Dependency-aware jobs, checkpoints and retries |
| Models | tier-based model interface | LiteLLM, Ollama | model selection by task complexity and provider portability |
| Tool access | disabled-by-default MCP registry | Filesystem, Fetch, Playwright, GitHub, Git | scoped external capabilities |
| Data | SQLite | DuckDB | run ledger and local analysis |
| Memory | SQLite FTS5 | Qdrant later | retrieval without loading all prior context |
| OCR | raw-first adapters | PaddleOCR, Tesseract, EasyOCR | multi-engine extraction and reconciliation |
| Automation | Python workflows | n8n | repeatable event and scheduled tasks |
| Evaluation | pytest and Ruff | Promptfoo, Langfuse | regression tests, traces and failure analysis |

Model usage is recorded only when a call supplies a SQLite usage store and run ID; the ledger captures provider-reported token counts and response cost. A recorded zero or missing cost is not a measurement of local electricity or hardware cost.

## Context efficiency

1. Persist full source data outside the prompt.
2. Retrieve only the records and source excerpts relevant to the current step.
3. Store compact intermediate summaries plus references to raw evidence.
4. Use deterministic code for parsing, joins, arithmetic and validation.
5. Escalate uncertain records to stronger models rather than sending every record to the strongest model.
6. Checkpoint each step so a retry does not redo completed work. Each run stores a fingerprint of its ordered step-name plan and explicit per-step revision. Increment a step's revision whenever its behavior, prompt, model choice or interpretation changes. Resumption rejects duplicate names, plan/revision changes and legacy checkpoints whose step order cannot be verified. Use a new run ID for intentional workflow changes.

## Trust boundaries

MCP servers run external processes. Filesystem access must be limited to project directories. Browser sessions should use isolated profiles. Database tools must target project databases. Credentials must stay in environment variables or secret stores. Purchases, public publishing, permission changes, destructive operations and external communications require distinct approval.
