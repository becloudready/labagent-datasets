---
doc_id: STD-SEC-002
title: Identity and Access Standard
doc_type: standard
version: 2.4
status: current
owner: Head of Security Architecture
effective_date: 2026-01-15
source_system: SharePoint
---

# STD-SEC-002 Identity and Access Standard (version 2.4)

## Requirements

- **R1 Workforce sign-in.** Workforce users MUST sign in through the corporate identity provider with single sign-on and multi-factor authentication.
- **R2 No shared accounts.** Shared or generic user accounts MUST NOT be used. Each action MUST be attributable to one person or one workload identity.
- **R3 Privileged access.** Privileged access MUST be granted through the privileged access management tool, just in time, for at most 8 hours per session.
- **R4 Workload identity.** Workloads MUST use platform workload identities. Long-lived access keys MUST NOT be created. Where a key is unavoidable it MUST be rotated at least every 90 days.
- **R5 Secrets.** Secrets MUST be stored in the approved secrets vault and MUST NOT be stored in source code, images, or configuration files.
- **R6 Access reviews.** Access to systems holding Restricted data MUST be reviewed every quarter. Access to all other systems MUST be reviewed every year.
- **R7 External API authentication.** APIs exposed to external parties MAY use OAuth 2.0 bearer access tokens when they are protected by the gateway web application firewall profile W2. Binding tokens to the client certificate (mutual TLS) is OPTIONAL.
- **R8 Customer identity.** Customer sign-in and registration MUST use the approved customer identity and access management platform.

## Notes

Requirements for how APIs are designed, versioned, and published are in the API Standard.
