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

Core storage, workflow, matching, and JSONL export functions need only Python and SQLite. Optional extras:

    pip install -e '.[llm]'          # LiteLLM model abstraction
    pip install -e '.[agents]'       # LangGraph orchestration
    pip install -e '.[mcp]'          # MCP client SDK
    pip install -e '.[browser]'      # Playwright browser automation
    pip install -e '.[ocr]'          # PaddleOCR/OpenCV
    pip install -e '.[data]'         # DuckDB/RapidFuzz
    pip install -e '.[observability]' # Langfuse client

## Model routing and token efficiency

Set AIOPS_MODEL_FAST, AIOPS_MODEL_STRONG and AIOPS_MODEL_DEEP in .env to LiteLLM model IDs. Hosted providers are blocked by default; explicitly set AIOPS_ALLOW_REMOTE_MODELS=true only when you accept possible provider charges. configs/litellm.config.example.yaml shows local Ollama routes. A router cannot add model context length or increase account/provider quota. The platform improves effective context use through retrieval, compact intermediate state, durable memory and checkpointing. AIOPS_MAX_TOKENS limits each completion request; it is not a token entitlement.

## Storage and resumable workflows

Default database: ./data/aiops.db. It stores workflow runs, per-step checkpoints and searchable memory. The dependency-free sequential engine is the default; LangGraph can be used for branching agent graphs.

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

    aiops init-db
    aiops csv-to-jsonl data/candidates.csv artifacts/candidates.jsonl
    aiops validate-jsonl artifacts/candidates.jsonl
    aiops run-status RUN_ID
    aiops ingest-csv data/candidates.csv candidates --key-field Candidate_ID
    aiops dataset-count candidates
    aiops usage-report

## Data safety

The public repo excludes data/, artifacts/, local DBs, environment files and secrets. Keep private OCR images and generated workbooks outside GitHub. CI runs lightweight unit tests; model weights and browser downloads are excluded.

## Local dataset store

Import CSV datasets into SQLite without dropping source columns. Original row content remains as JSON.

    aiops ingest-csv data/candidates.csv candidates --key-field Candidate_ID
    aiops dataset-count candidates

Dataset import is idempotent for a stable key field. Private datasets stay local and are excluded from Git.

## Laptop research operations

The private laptop OCR delivery has its own audited workbench and an ingestion runbook. Do not add its screenshots, workbook, CSVs, SQLite database or generated exports to this public repository.

- [Laptop dataset runbook](docs/LAPTOP_DATASET_RUNBOOK.md): inspect the private read-only SQLite snapshot, import compatible CSV batches, and run coverage checks.
- [Research fact schema](docs/RESEARCH_FACT_SCHEMA.md): capture exact-SKU/model-family scope, one fact per source, price-type separation and conflict handling.
- [Official model source audit — 2026-11-02](docs/OFFICIAL_MODEL_SOURCE_AUDIT_2026-11-02.md): scoped manufacturer-source checks and unresolved SKU/OS conflicts; no inferred price updates.
- [Local deployment preflight](docs/LOCAL_DEPLOYMENT_PREFLIGHT.md): host setup, local-only model routing, MCP/browser boundaries, n8n hardening, backups and release gates.
- [Next analysis session checklist](docs/NEXT_ANALYSIS_SESSION_CHECKLIST.md): the exact read-back, reconciliation, enrichment, database and release steps; avoids rebuilding an already-delivered workbook.
