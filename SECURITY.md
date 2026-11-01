# Security Policy

## Supported code

Security fixes are intended for the latest code on the `main` branch. Older commits and unpublished development branches are not maintained release lines.

## Automated analysis

The repository runs CodeQL analysis for Python on pushes to `main`, pull requests targeting `main` and a weekly schedule. Pull requests also run dependency review against new or updated runtime, development and unknown-scope dependencies, failing on newly introduced high or critical vulnerabilities and showing patched versions where available. These automated checks help identify some risks; they do not establish that the code is vulnerability-free. Review alerts in the GitHub Security tab and follow the private disclosure process below for new findings.

## Reporting a vulnerability

Do not publish exploit details, credentials, tokens, private laptop records or sensitive screenshots in a public GitHub issue or pull request.

When GitHub private vulnerability reporting is enabled for this repository, use the repository's **Security** tab and its private vulnerability-reporting flow. If that route is not available, contact the repository owner through the GitHub profile before disclosing technical details publicly.

Include the affected commit or version, impact, reproduction conditions and a minimal sanitized proof of concept. Do not include real credentials or user data.

## Scope and operational boundaries

- The project is local-first; optional remote model providers are disabled by default.
- MCP servers and automation services are opt-in and must be scoped to the minimum resources required.
- Local datasets, screenshots, databases, logs, model prompts and credentials must remain outside the public repository unless explicitly sanitized and approved for publication.
- Never submit real user laptop OCR evidence or the private workbench database as a vulnerability attachment.

No response-time or remediation SLA is implied by this policy.
