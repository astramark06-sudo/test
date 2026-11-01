# Operator State — 2026-11-02

This is the operational handoff for the current platform and the saved private laptop research delivery. It separates work that is implemented and verified from work that still requires the owner's settings or a connected local host.

## Canonical code state

- Repository: https://github.com/astramark06-sudo/test
- Default branch: `main`
- Current main commit at this handoff: `f86df391b5264a8584fd865158e3169a52a9a718`
- Post-merge CI: https://github.com/astramark06-sudo/test/actions/runs/41341519500
- Post-merge CodeQL: https://github.com/astramark06-sudo/test/actions/runs/41341519485

The post-merge CI run passed on Python 3.10, 3.11, 3.12 and 3.13. Every matrix job completed:

1. Install build frontend and `.[dev,data]`.
2. `pip check`.
3. Ruff.
4. Full pytest suite.
5. Build distributable wheel.
6. `aiops --help` entry-point smoke test.
7. `aiops doctor --json` smoke test against a deliberately missing DB path; no DB was created.

CodeQL v4 Python analysis succeeded on the main branch. A successful scan run does not prove that the repository has zero security findings; review alerts in GitHub's Security tab.

## Implemented platform protections

- Python CI matrix covers declared Python 3.10+ support through Python 3.13.
- Dependabot opens grouped weekly update PRs for pip dependencies and GitHub Actions. There is no auto-merge.
- CodeQL runs on main pushes, main pull requests, weekly schedule and manual dispatch.
- Generic `aiops ingest-csv` uses the shared strict preflight validator before constructing/writing SQLite. It rejects malformed structure, invalid/duplicate stable keys and missing inputs. Keyless exact duplicate-content rows are reported.
- The dedicated multi-file laptop importer preflights every present CSV before writing and commits dataset/source rows in one SQLite transaction.
- `aiops doctor` and `aiops doctor --json` report host OS/architecture, logical CPU count, physical RAM where available, disk free space, GPU inventory utility availability, Python/SQLite, optional package presence, configuration files, remote-model opt-in, Ollama endpoint locality and existing DB quick_check.
- Doctor does not make network calls, execute GPU utilities, expose secret values, create files or write to the database.
- Contributor, pull-request and private vulnerability disclosure guidance is present.
- Free-tier comparison is documented; local SQLite remains canonical.

## Owner-side GitHub settings still required

### 1. Enable Dependency Graph

PR #10 adds GitHub Dependency Review v5:

https://github.com/astramark06-sudo/test/pull/10

Its first check failed because the repository's Dependency Graph is disabled. This was a prerequisite error, not a reported vulnerable dependency. The workflow did not complete dependency analysis.

Owner action:

1. Open https://github.com/astramark06-sudo/test/settings/security_analysis
2. Under **Dependency graph**, enable the graph for the repository.
3. Return to PR #10 and re-run failed checks.
4. Merge only after the Dependency Review check passes.

The workflow reviews runtime, development and unknown dependency scopes, and fails on newly introduced high/critical known vulnerabilities. It shows patched versions where available.

### 2. Protect the main branch

Current read-only GitHub API state: `protected=false`, `rulesets=[]`.

After dependency review is enabled, configure a branch ruleset for `main`:

- Require pull requests before merging.
- Require the four CI checks: `test (3.10)`, `test (3.11)`, `test (3.12)`, `test (3.13)`.
- Require CodeQL `Analyze Python`.
- Require Dependency Review `Review dependency changes` after it becomes green.
- Block force pushes and branch deletion.
- Require the branch to be up to date only if merge queue/update behavior is configured and tested.

Settings page: https://github.com/astramark06-sudo/test/settings/branches

The connected GitHub operations interface can read settings and change repository content/PRs, but it does not expose ruleset writes.

### 3. Repository visibility and license

- Repository remains public. The connected integration does not expose a public-to-private visibility change. No private laptop data is committed.
- No project license has been chosen or added. Do not assume MIT or another license. Owner chooses before inviting external reuse/contributions that depend on licensing terms.
- Private vulnerability reporting may need enabling in the Security settings if the private reporting route is not already available.

## Host installation status

No package, model, MCP process, Playwright browser, n8n service or Cloudflare/Neon/Supabase resource has been installed/provisioned on the user's physical device. This session has no device shell connection. Configuration and source code are prepared, but do not label the host runtime as installed.

After cloning/pulling the current repository on the host:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data]"
aiops doctor --project-root . --db ./data/aiops.db --json
ruff check .
pytest -q
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

Review doctor output before installing Ollama or model weights. It reports resource headroom but only detects whether GPU inventory tools exist; exact GPU/VRAM must be confirmed through the host OS/vendor utility. Never automatically download a large model before checking available RAM, VRAM and disk.

## Private laptop research baseline

All source files remain in the Library under `/AI Operations Platform Deliverables`. The authoritative final release is:

- `laptop_inventory_reconciled_348.xlsx` — 12 tabs.
- `laptop-research-evidence-bundle.zip`.
- `ocr_candidates_validated.jsonl` — 348 full-fidelity candidate records.
- `tesseract_segment_audit_all_80_tiles.csv`.
- `aiops-workbench-data-bundle.zip`.
- `aiops_platform_workbench.sqlite3` and read-only `workbench_cli.py`.
- Both SHA-256 manifests and readme files.

Baseline counts:

- 348 OCR candidate IDs; not 348 verified unique SKUs.
- 220 detailed listing rows from 99 OCR segments/four screenshots.
- 215 conservative candidate-to-listing links, 133 unmatched candidates and five unpaired detailed listings.
- 195 OCR-observed price values carried in the final workbook; researched price fields remain distinct/blank unless source-backed.
- 89 configuration rows, 39 CPU benchmark rows, 27 source references.
- 80 independent Tesseract tiles, 16,044 words and mean confidence 79.91.
- One clipped tail tile is unresolved and has no safe product identity or assigned price.

## Next data-analysis session — do not rebuild

Follow [Next Analysis Session Checklist](NEXT_ANALYSIS_SESSION_CHECKLIST.md). The critical additional guard is the version mismatch:

- The earlier importer profile contains a 199-row `ocr_prices_199.csv` table and 299 screenshot price-evidence rows.
- The final 12-tab workbook carries 195 OCR-observed price values.
- Those are different artifact versions and row definitions. Do not merge totals or assume five values are missing until row-level source/version/key reconciliation proves it.

Start with saved SHA-256 manifests, workbook tab/row read-back, JSONL count and read-only SQLite QA. Make copies before imports. Compare the 199/299 intermediate evidence extracts with the 195 final-workbook values and determine whether every final value is represented, transformed, excluded or unresolved. Do not populate current retailer prices; the final delivery instruction preserves OCR price evidence and keeps researched prices separate. Keep the clipped-tail gap open unless the actual pixels establish identity.

## Free-tier infrastructure decision

No cloud service is deployed. Use local SQLite by default. If remote synchronization becomes a real requirement, the documented first candidate is Neon Free as a Postgres sidecar. Use Cloudflare Workers only for a thin API; do not run OCR/model inference there. Do not create an account, database, endpoint or billing method before a specific need, privacy review, quota check and backup plan exist.
