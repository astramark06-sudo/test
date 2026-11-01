# Contributing

## Development setup

Use Python 3.10 or newer. The CI matrix tests Python 3.10, 3.11, 3.12 and 3.13.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data]"
aiops doctor --project-root .
ruff check .
pytest -q
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

The core platform does not require a hosted model, paid API, cloud database or downloaded model weights. Keep remote model access disabled unless a task explicitly requires it and the provider costs/data terms have been reviewed.

## Pull requests

- Keep changes focused and explain the behavior being changed.
- Add or update deterministic tests for code changes.
- Run Ruff and pytest locally; CI repeats both across the supported Python versions.
- Preserve backward compatibility or document an intentional migration.
- Do not commit `.env`, credentials, tokens, personal browser profiles, databases, screenshots, user datasets, workbook exports or model weights.
- Use synthetic or redacted fixtures for issue reproduction. Never attach the private laptop research bundle to a public issue or pull request.
- Keep the original OCR/source evidence immutable. Put transformations in derived fields or exports.
- Record source URL, retrieval date, exact model/SKU scope and confidence for researched facts.
- Keep OCR-observed prices, researched prices, bank offers, exchange values and discounts in distinct fields. Never infer an exact SKU from title similarity alone.
- Do not enable remote providers, external MCP servers, browser sessions or persistent automation by default.

## Dataset and schema changes

- Validate the entire input batch before opening a write transaction.
- Prefer stable record keys. If a dataset has no stable key, document its content-hash identity and duplicate-row behavior.
- Make bundle imports atomic and idempotent.
- Keep provenance, unresolved conflicts and review status recoverable.
- Update the laptop runbook and schema documentation when import contracts change.
- Never replace or silently normalize the raw source value.

## Dependency changes

Dependabot opens grouped weekly pull requests for Python and GitHub Actions dependencies. Review changelogs and CI before merging. Automated merging is intentionally disabled.
