# Optional free-tier cloud components — 2026-11-02

## Decision

Keep the local SQLite workbench as the canonical system of record. Do not provision a cloud database or public API merely because a free tier exists. Add remote infrastructure only when there is a concrete requirement for multi-device synchronization, shared access, authentication or a publicly reachable lightweight endpoint.

The laptop OCR screenshots, raw OCR, candidate rows, source evidence, workbooks and private SQLite snapshot stay local/private. A cloud service must not become the primary store for that evidence without a separate data-protection decision.

## Current provider comparison

Limits below were checked against the providers' official documentation on 2026-11-02. Free-plan terms can change; re-check the linked page before creating a project.

| Service | Current published free allowance | Appropriate role | Material constraints |
|---|---|---|---|
| Neon Postgres Free | 1 GB storage/project; 100 compute-hours/project/month; 10 branches/project; 5 GB public transfer/project/month; up to 2 CU; compute scales to zero after 5 minutes | Preferred optional Postgres sidecar for low-traffic shared application metadata or sync | Compute suspends after the monthly allowance; storage writes that exceed the free cap fail. No always-on guarantee. |
| Supabase Free | 500 MB database/project; 5 GB egress; 1 GB file storage; 50,000 monthly active users; 2 active projects | Choose only when integrated Auth, Storage and Realtime materially reduce application work | Projects pause after one week of inactivity. Database storage is lower than Neon's current Free allowance. |
| Cloudflare Workers Free | 100,000 requests/day; 10 ms CPU/request; 128 MB memory; 50 subrequests/request | Lightweight authenticated API, webhooks or thin serverless adapter | Not suitable for heavy OCR, long-running model inference or large synchronous jobs. |
| Cloudflare D1 Free | 10 databases/account; 500 MB/database; 5 GB total storage/account; 5 million rows read/day; 100,000 rows written/day; 7-day Time Travel | Small edge-side SQL metadata store when the API is already on Workers | SQLite-compatible edge database, not PostgreSQL. Storage and daily read/write caps apply. |

## Recommended order

1. **Now:** use local SQLite and existing Airtable/GitHub connectors for operations metadata. The user already has a local-first workbench and connected operational tracking.
2. **Only when remote synchronization is needed:** evaluate Neon Free as the first Postgres candidate. Start with non-sensitive metadata, confirm project region and connection policy, use a restricted database role and keep a private local backup.
3. **Only when an HTTP endpoint is needed:** evaluate Cloudflare Workers Free as a thin stateless API. Apply authentication, rate limits, input-size limits and request logging that excludes private payloads.
4. **Use Supabase instead of Neon** only when its bundled Auth, file storage or Realtime features are needed enough to justify its smaller database allowance and inactivity pause.
5. **Avoid duplicate databases.** Do not keep the same canonical dataset independently in SQLite, Neon, Supabase and D1. Define one system of record and explicit replication direction before syncing.

## Security and cost controls

- No cloud account, database, endpoint, API key or billing method has been created or configured by this work.
- Keep private laptop data and screenshots out of cloud test payloads. Use synthetic test records for endpoint validation.
- Do not attach a payment method, choose a paid plan, enable paid overages or deploy a public endpoint as part of a free-tier experiment.
- Keep API keys in local environment variables or a secret manager. Never commit `.env` or credentials.
- Use least-privilege database users, TLS, authentication, request-size limits, rate limits and a backup/export path.
- Set usage alerts where the provider exposes them; treat free quotas as hard ceilings, not available paid credit.
- Re-check the live plan before deployment because limits and model/provider availability can change.

## Official sources

- Neon, “Neon gives you 100 projects for free, with 1 GB of Postgres storage each” (2026-10-02): https://neon.com/blog/neon-free-plan-1-gb-per-project
- Neon Free-plan limits: https://github.com/neondatabase/website/blob/main/content/faqs/free-plan-limits-and-quotas.md
- Supabase pricing: https://supabase.com/pricing
- Supabase billing and quotas: https://supabase.com/docs/guides/platform/billing-on-supabase
- Cloudflare Workers limits (updated 2026-10-29): https://developers.cloudflare.com/workers/platform/limits/
- Cloudflare Workers pricing: https://developers.cloudflare.com/workers/platform/pricing/
- Cloudflare D1 limits (updated 2026-10-30): https://developers.cloudflare.com/d1/platform/limits/
