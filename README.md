# AI Operations Platform

A local-first AI workbench for auditable extraction, research, workflow automation and multi-model operations. Core features run without paid APIs or hosted services.

## Core design rules

- Preserve raw source data and OCR outputs.
- Keep OCR-observed prices separate from researched/current prices.
- Never silently resolve conflicting OCR readings or ambiguous laptop configurations.
- Route routine tasks to smaller/local models and reserve stronger models for hard cases and final review.
- Use deterministic code and retrieval for parsing, joins, calculations and long-term context.
- Checkpoint long workflows in SQLite so interrupted tasks can resume.
- Do not commit user datasets, screenshots, databases, artifacts, credentials or .env files to this public repository.

## Quick start

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e '.[dev]'
    cp .env.example .env
    aiops init-db
    pytest -q
    ruff check .

Core storage, workflow, matching, JSONL, database-backup and file-manifest functions use the base Python dependencies (PyYAML and python-dotenv) plus SQLite; no model weights or hosted services are required. Optional extras:

    pip install -e '.[llm]'          # LiteLLM model abstraction
    pip install -e '.[agents]'       # LangGraph orchestration
    pip install -e '.[mcp]'          # MCP client SDK
    pip install -e '.[browser]'      # Playwright browser automation
    pip install -e '.[ocr]'          # PaddleOCR 3.x + PaddlePaddle CPU + OpenCV
    pip install -e '.[data]'         # DuckDB/RapidFuzz
    pip install -e '.[observability]' # Langfuse client

See [OCR engine compatibility](docs/OCR_ENGINE_COMPATIBILITY.md) for the pinned PaddleOCR 3.x API, CPU install path, model-download behavior and OCR adapter contract.

The Python entry points load `.env` from the current project directory automatically, without overriding variables already exported by the shell. Set `AIOPS_ENV_FILE` in the shell to use a different environment-file path. Keep `.env` local; never commit it.

## Model routing and token efficiency

Set AIOPS_MODEL_FAST, AIOPS_MODEL_STRONG and AIOPS_MODEL_DEEP in .env to LiteLLM model IDs. Hosted providers are blocked by default. Local-only mode accepts `ollama/` and `ollama_chat/` using `OLLAMA_BASE_URL` (default `http://localhost:11434`); `lm_studio/` and `vllm/` require `LM_STUDIO_BASE_URL` or `VLLM_BASE_URL`. For llama.cpp and other OpenAI-compatible local servers, use LiteLLM's `custom_openai/` prefix with `CUSTOM_OPENAI_BASE_URL`. Every configured or per-call `api_base` / `base_url` must resolve to a loopback host. `hosted_vllm/` is not treated as local. Set `AIOPS_ALLOW_REMOTE_MODELS=true` only when provider charges and data handling are explicitly accepted; this opts out of the local-only boundary. A router cannot add model context length or increase account/provider quota. The platform improves effective context use through retrieval, compact intermediate state, durable memory and checkpointing. `AIOPS_MAX_TOKENS` limits each completion request; it is not a token entitlement.

## Storage and resumable workflows

Default database: `./data/aiops.db`. It stores workflow runs, per-step checkpoints and searchable memory. The dependency-free sequential engine is the default; LangGraph can be used for branching agent graphs. A run locks its workflow name, ordered unique step-name plan and explicit per-step revision. Increment a step's `revision` whenever its behavior, prompt, model choice or interpretation changes; reusing a run ID with a changed plan/revision is rejected. Create a new run ID for intentional changes. Legacy checkpoints without a saved plan are not resumed automatically because their original step order cannot be proved.

    from aiops.storage.sqlite import SQLiteStore
    from aiops.workflows.engine import Step, WorkflowEngine
    store = SQLiteStore('./data/aiops.db')
    result = WorkflowEngine(store).run('example', {'text':'hello'}, [
        Step('normalize', lambda s: {'normalized': s['text'].strip().lower()}),
    ])

## MCP and external apps

Copy configs/mcp_servers.example.json to a local file and enable only scoped servers. MCP servers execute as external processes and may have broad file, browser or database permissions. Filesystem access is scoped to project directories. Browser automation should use an isolated profile. Prefer the connected GitHub App and existing Airtable integration over duplicate credentials.

Useful optional apps: GitHub for source control/CI, Airtable for project/source tracking, n8n for local event automation, Langfuse for traces, and Playwright MCP for browser research. Start n8n after configuring .env:

    docker compose --profile automation -f deploy/docker-compose.yml up -d

Playwright MCP setup: https://playwright.dev/docs/getting-started-mcp. The official MCP Fetch server can be run with uvx mcp-server-fetch; it protects private IP ranges by default.

## CLI

    aiops doctor
    aiops doctor --json
    aiops backup-db ./backups/aiops-YYYYMMDD.sqlite --db ./data/aiops.db
    aiops hash-tree ./release ./release.manifest.json
    aiops verify-manifest ./release ./release.manifest.json
    aiops init-db
    aiops csv-to-jsonl data/candidates.csv artifacts/candidates.jsonl
    aiops validate-jsonl artifacts/candidates.jsonl
    aiops run-status RUN_ID
    aiops ingest-csv data/candidates.csv candidates --key-field Candidate_ID
    aiops dataset-count candidates
    aiops usage-report

When using `ModelRouter.complete`, pass `usage_store=SQLiteStore(...)` and a stable `run_id` to record observed prompt/completion tokens and LiteLLM-reported response cost. Usage recording is opt-in; calls without a store do not create ledger entries.

## Data safety

The public repo excludes data/, artifacts/, local DBs, environment files and secrets. Keep private OCR images and generated workbooks outside GitHub. CI runs Ruff and pytest across Python 3.10, 3.11, 3.12 and 3.13. CodeQL scans Python code on main changes, pull requests and a weekly schedule; review findings under the repository Security tab. Model weights and browser downloads are excluded.

## Local dataset store

Import CSV datasets into SQLite without dropping source columns. Original row content remains as JSON.

    aiops ingest-csv data/candidates.csv candidates --key-field Candidate_ID
    aiops dataset-count candidates

`aiops doctor` performs read-only host checks: OS/architecture, logical CPU count, physical RAM where the OS exposes it, free disk space, GPU inventory-tool availability, Python and SQLite versions, optional integration module versions, project configuration-file presence, remote-model opt-in state, all supported local inference endpoint locality, n8n encryption-key readiness without exposing the key, and an existing SQLite database's quick integrity check. It does not contact external services, read or print secret values, create directories, or modify the database. Run it from the project root before enabling optional components.

Before creating or writing to the SQLite database, `aiops ingest-csv` validates the complete CSV: it requires a header, rejects empty or duplicate column names, checks every row width, and validates a supplied stable-key column for missing, blank, whitespace-padded or duplicate values. Keyless imports use deterministic row-content hashes; exact duplicate-content rows are reported because identical rows share one stored key. A failed preflight leaves the target database untouched.

`aiops backup-db OUTPUT --db SOURCE` uses SQLite's online backup API, opens the source read-only, checks the finished copy with `PRAGMA integrity_check`, then atomically places it at the destination. Existing destinations are refused unless `--overwrite` is supplied; a failed backup leaves the existing destination unchanged.

`aiops hash-tree DIRECTORY OUTPUT` writes a sorted SHA-256/size manifest outside the inventoried folder. `aiops verify-manifest DIRECTORY MANIFEST` checks every hash and size and also detects missing, unlisted or symlinked files. Keep the manifest beside—not inside—the immutable source folder.

Dataset import is idempotent for a stable key field. Private datasets stay local and are excluded from Git.

## Laptop research operations

The private laptop OCR delivery has its own audited workbench and an ingestion runbook. Do not add its screenshots, workbook, CSVs, SQLite database or generated exports to this public repository.

- [Laptop dataset runbook](docs/LAPTOP_DATASET_RUNBOOK.md): inspect the private read-only SQLite snapshot, import compatible CSV batches, and run coverage checks.
- [Research fact schema](docs/RESEARCH_FACT_SCHEMA.md): capture exact-SKU/model-family scope, one fact per source, price-type separation and conflict handling.
- [OCR engine compatibility](docs/OCR_ENGINE_COMPATIBILITY.md): PaddleOCR 3.x API, compatible CPU runtime and OCR result normalization.
- [Laptop release notes — 2026-11-02](docs/LAPTOP_RELEASE_2026-11-02.md): verified private workbook/database release counts, scope, checksums and data-handling rules.
- [Official model source audit — 2026-11-02](docs/OFFICIAL_MODEL_SOURCE_AUDIT_2026-11-02.md): scoped manufacturer-source checks and unresolved SKU/OS conflicts; no inferred price updates.
- [Local deployment preflight](docs/LOCAL_DEPLOYMENT_PREFLIGHT.md): host setup, local-only model routing, MCP/browser boundaries, n8n hardening, backups and release gates.
- [Optional free-tier cloud services](docs/OPTIONAL_FREE_CLOUD_SERVICES_2026-11-02.md): current Neon, Supabase, Cloudflare Workers and D1 limits; local-first data boundaries and cost controls.
- [Next analysis session checklist](docs/NEXT_ANALYSIS_SESSION_CHECKLIST.md): the exact read-back, reconciliation, enrichment, database and release steps; avoids rebuilding an already-delivered workbook.
- [Open issues and review queue](docs/OPEN_ISSUES_AND_REVIEW_QUEUE.md): prioritized SKU, source-conflict, reconciliation, price and benchmark issues.
