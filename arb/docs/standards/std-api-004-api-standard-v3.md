---
doc_id: STD-API-004
title: API Standard
doc_type: standard
version: 3.0
status: current
owner: Head of Integration Architecture
effective_date: 2026-03-01
supersedes: STD-API-004 version 2.1
source_system: SharePoint
---

# STD-API-004 API Standard (version 3.0)

Version 3.0 replaces version 2.1 from 1 March 2026. The main change is that API keys are no longer allowed for partner access.

## Requirements

- **R1 Design first.** Every API MUST have an OpenAPI 3 specification that is reviewed before implementation.
- **R2 Versioning.** The major version MUST be part of the path, for example /v1/. A deprecated version MUST stay available for at least 6 months after the notice.
- **R3 Gateway.** External APIs MUST be published only through the enterprise API gateway.
- **R4 Rate limits.** The default rate limit is 100 requests per second per client unless a different limit is agreed in the submission.
- **R5 Idempotency.** Operations that create resources MUST accept an idempotency key.
- **R6 External authentication.** External APIs MUST authenticate clients with OAuth 2.0 client credentials and MUST bind access tokens to the client certificate using mutual TLS (RFC 8705). API keys MUST NOT be used.
- **R7 Transport security.** TLS 1.2 is the minimum. TLS 1.3 is preferred.
- **R8 Pagination.** List operations MUST use cursor-based pagination.
- **R9 Errors.** Errors MUST use the problem details format of RFC 9457.
- **R10 No personal data in URLs.** Personal data MUST NOT appear in paths or query strings.
