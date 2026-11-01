# AI Operations Platform

A zero-budget, modular AI operations workspace. The initial implementation prioritizes reliable document OCR, structured extraction, validation, and auditable exports.

## Initial priorities

1. Preserve source files and raw OCR output.
2. Reconcile multiple OCR engines without discarding disagreements.
3. Keep OCR-derived prices separate from researched prices.
4. Export validated records to CSV, JSONL, and Excel.
5. Run lightweight tests in GitHub Actions; keep heavyweight OCR models out of CI.

## Cost policy

No paid services, subscriptions, or cloud resources are assumed. Local CPU execution is the default; hosted free tiers are optional and quota-limited.
