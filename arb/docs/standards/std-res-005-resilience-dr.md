---
doc_id: STD-RES-005
title: Resilience and Disaster Recovery Standard
doc_type: standard
version: 3.1
status: current
owner: Head of Infrastructure Architecture
effective_date: 2026-02-01
source_system: SharePoint
---

# STD-RES-005 Resilience and Disaster Recovery Standard (version 3.1)

## Service tiers and recovery objectives

| Tier | Meaning | Recovery time objective (RTO) | Recovery point objective (RPO) |
|---|---|---|---|
| Tier 1 | Mission critical, direct customer or revenue impact | 60 minutes | 5 minutes |
| Tier 2 | Business critical | 4 hours | 1 hour |
| Tier 3 | Business important | 24 hours | 24 hours |
| Tier 4 | Best effort | 5 days | 24 hours |

## Requirements

- **R1 Tier assignment.** Every service MUST have a tier set by a business impact analysis that the business owner has signed.
- **R2 Design to the tier.** The recovery design MUST meet the RTO and RPO of the tier. The design MUST state how the objectives are met.
- **R3 Recovery testing.** Recovery MUST be tested at least once a year for Tier 1 and Tier 2 services, and the test results MUST be kept as evidence for Gate 3.
- **R4 Runbooks.** Every Tier 1 to Tier 3 service MUST have a recovery runbook that was reviewed in the last 12 months.
- **R5 Backups.** Backups of Restricted data MUST be immutable and stored in a separate account.
- **R6 Dependencies.** A service MUST NOT depend on a service of a lower tier for its critical functions.
