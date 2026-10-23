---
doc_id: STD-API-004-V2.1
title: API Standard (superseded version 2.1)
doc_type: standard
version: 2.1
status: superseded
owner: Head of Integration Architecture
effective_date: 2025-06-01
superseded_by: STD-API-004 version 3.0
source_system: SharePoint
---

# STD-API-004 API Standard (version 2.1) SUPERSEDED on 1 March 2026

This version is kept for reference only. It is replaced by version 3.0. Do not use it to review new submissions.

## Requirements

- **R1 Design first.** Every API MUST have an OpenAPI 3 specification.
- **R2 Versioning.** The major version MUST be part of the path. A deprecated version MUST stay available for 3 months after the notice.
- **R3 Gateway.** External APIs MUST be published through the enterprise API gateway.
- **R4 Rate limits.** The default rate limit is 50 requests per second per client.
- **R6 External authentication.** External APIs MUST use OAuth 2.0 client credentials. Partner integrations MAY use API keys when the partner source addresses are on an allow list. Mutual TLS is RECOMMENDED but not required.
- **R7 Transport security.** TLS 1.2 is the minimum.
