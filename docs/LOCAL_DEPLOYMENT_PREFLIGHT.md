# Local Deployment Preflight

The canonical implementation is maintained in the public GitHub repository. This document is a host-side checklist; it does not imply that services, model weights, browser binaries, credentials or background agents have been installed on the user's device.

## 1. Core environment

Required for the core local platform:

- Python 3.10 or newer. CI tests Python 3.10, 3.11, 3.12 and 3.13; the current main-branch matrix passes on all four.
- SQLite (bundled with standard Python builds).
- Git to clone/pull the source.
- No hosted LLM account, API key, paid service or cloud database is required for the core workflow.

Recommended isolated installation:

```bash
git clone https://github.com/astramark06-sudo/test.git
cd test
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data]"
ruff check .
pytest -q
aiops doctor
aiops doctor --json
aiops init-db
```

Run `aiops doctor` from the repository root before installing optional components. It reports OS and architecture, logical CPU count, physical RAM where available through standard OS APIs, free disk space, GPU inventory-tool availability, core runtime versions, optional module availability, configuration-file presence, remote-model opt-in state, Ollama endpoint locality, n8n encryption-key readiness without printing the key, and the quick integrity status of an existing database. It does not execute GPU inventory commands; use the host OS device manager or vendor utility to confirm the exact GPU and VRAM. The check is read-only: it does not contact external services, display secret values, create directories or modify the database.

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`. Keep the virtual environment local and do not commit it.

The Python CLI, model router, MCP client and observability helper load the local `.env` file automatically. Variables already exported in the shell take precedence. The optional n8n service reads the same file through Docker Compose. Keep secrets in the ignored local file.

### Repository maintenance

- Dependabot checks Python dependencies and GitHub Actions weekly. Related updates are grouped into reviewable pull requests; auto-merge is not enabled.
- The `main` branch currently has no branch protection or repository ruleset. Recommended owner configuration: require a pull request and successful CI matrix jobs for Python 3.10, 3.11, 3.12 and 3.13; block force-pushes and branch deletion.
- This repository is public and currently has no `LICENSE` file. Keep all private laptop data out of it. Choose a license only when the owner decides what external reuse to permit.

## 2. Private research data

- Keep the evidence bundle and workbook in a private local directory, not the public repository.
- Extract the separate read-only SQLite workbench bundle for inspection; do not use it as a write target.
- For a new import/reprocessing run, copy the source CSV batch to a versioned private input directory and preserve that input directory unchanged.
- Save the import report and a SHA-256 manifest beside the batch.
- Import into a new database or a verified backup copy first. The canonical importer upserts by key; reusing a key replaces its stored payload.
- Do not load screenshots or private OCR files into GitHub issues, Actions artifacts, public logs or model-provider prompts unless the destination has been explicitly reviewed.

See [Laptop dataset runbook](LAPTOP_DATASET_RUNBOOK.md) and [Research fact schema](RESEARCH_FACT_SCHEMA.md).

## 3. Model runtime

Default posture: local-only; remote providers remain blocked.

1. Leave `AIOPS_ALLOW_REMOTE_MODELS=false`.
2. Keep `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` empty unless remote access is separately approved and cost understood.
3. The local-only router permits `ollama/` and `ollama_chat/` at `OLLAMA_BASE_URL` (default `http://localhost:11434`). It permits `lm_studio/`, `vllm/` and `llamacpp/` only when their respective `LM_STUDIO_BASE_URL`, `VLLM_BASE_URL` or `LLAMACPP_BASE_URL` is explicitly set to a loopback URL. `hosted_vllm/` is not a local backend.
4. Per-call `api_base` and `base_url` overrides are also required to be loopback URLs. Non-loopback hosts are rejected before the provider call.
5. Set `AIOPS_ALLOW_REMOTE_MODELS=true` only after explicitly accepting provider cost, terms and data handling; this disables the local-only endpoint restrictions.
6. Pick model weights to fit actual host RAM/VRAM and task needs. Do not automatically download large models.
7. Keep prompts and retrieved context compact; send row batches with stable IDs and source pointers; persist full evidence outside model context.
8. Record actual observed token usage. A router, model alias or `AIOPS_MAX_TOKENS` setting does not increase the ChatGPT account quota or the model/provider context window.

No model weights are included in this repository.

### OCR runtime

- The PaddleOCR adapter targets PaddleOCR 3.7.x and pins PaddlePaddle 3.2.0, the CPU version shown by PaddleOCR's current quick start. The OCR extra pins the PaddleOCR 3.7 minor line.
- Install the CPU-oriented default only when OCR is needed: `python -m pip install -e ".[ocr]"`.
- The first PaddleOCR run may download model weights. Check free disk and RAM first; do not auto-download on the user's device.
- GPU runtime installation is host-specific. Confirm OS, Python, CUDA and GPU compatibility against the official PaddlePaddle install matrix before replacing CPU wheels.
- CI tests normalization with mocked results. A real-image OCR smoke test is still required on the target host and must log package/model versions and device without modifying original images.

See [OCR engine compatibility](OCR_ENGINE_COMPATIBILITY.md).

## 4. MCP and browser safety

The example MCP registry keeps every server disabled by default. Enable only the one required for a specific workflow.

- Filesystem server: allow only a dedicated project data and artifact directory; never the home directory, credential folders or whole disk.
- Fetch server: public web pages only; do not permit access to private IP ranges or local control planes.
- Playwright: isolated browser profile, no personal logged-in sessions, no saved passwords, no payment profile.
- GitHub MCP: prefer the existing connected GitHub App over a second personal access token. If a PAT is unavoidable, use least privilege and short expiry.
- Git MCP: scope it to this repository only.
- Do not enable MCP tools solely to duplicate access already available through an approved connector.

## 5. n8n local automation

The optional Compose profile binds n8n to loopback `127.0.0.1`; it is not intended to be exposed directly to a public network.

Before startup:

- Set a unique high-entropy `N8N_ENCRYPTION_KEY` in the local, ignored `.env`.
- Back up the n8n volume and key together; the key is required to decrypt stored credentials.
- Review workflow nodes and credentials before activation.
- Do not expose the service via router port-forwarding.
- Pin the n8n image to a reviewed release or digest before a production deployment; the current example uses the moving `latest` tag for convenience.
- Start only when required: `docker compose --profile automation -f deploy/docker-compose.yml up -d`.

Stop with:

```bash
docker compose --profile automation -f deploy/docker-compose.yml down
```

The named volume remains unless explicitly removed; do not delete it as a routine stop operation.

## 6. Storage, backup and recovery

- Keep `data/` and `artifacts/` outside version control.
- Back up SQLite databases before migrations, imports or schema changes.
- Use `aiops backup-db ./backups/<name>.sqlite --db ./data/aiops.db` to create an online backup and verify its integrity. The command refuses an existing destination unless `--overwrite` is explicitly supplied; it never overwrites the source.
- Retain an immutable copy of the original input batch and its hash.
- Use separate development and working databases; never test migrations against the only copy.
- Verify backups with SQLite integrity checks and restore tests on a separate copy.
- Store workflow run IDs and checkpoint information with delivery manifests so a failed step can resume without repeating completed work.
- Keep outputs and their source manifest together; record hashes for every release artifact.

## 7. Observability and evaluation

Optional Langfuse can record traces, latency and model/provider usage. Keep raw OCR and private prompts out of external telemetry unless the data handling terms and destination have been reviewed. For local-first usage, keep structured run records in SQLite and run the deterministic tests before adding a remote observability service.

Promptfoo and model-based evaluation are optional. The CI baseline remains Ruff and pytest. Add deterministic fixture tests for parser, matching, reconciliation and price classification before enabling automated bulk enrichment.

## 8. Release gate

Do not call a release complete until:

- CI is green for the exact commit.
- The local environment can initialize the database and pass tests.
- Secrets are absent from Git history and tracked files.
- MCP servers are disabled unless specifically required and scoped.
- n8n is loopback-only with an encryption key if used.
- Remote model access is disabled unless explicitly approved.
- Private datasets stay local.
- A recovery copy and SHA-256 manifest exist.
- The release notes distinguish built code, configured examples, installed services and actually tested runtime integrations.

## Not completed from this environment

The user's phone/PC filesystem and shell are not connected to this repository session. Therefore this session cannot truthfully claim that Python packages, Ollama, model weights, MCP processes, Playwright browsers or n8n have been installed or started on the user's device. This preflight makes those steps reproducible when performed on the host.
