---
doc_id: STD-OBS-006
title: Logging and Observability Standard
doc_type: standard
version: 2.2
status: current
owner: Head of Application Architecture
effective_date: 2026-02-01
source_system: SharePoint
---

# STD-OBS-006 Logging and Observability Standard (version 2.2)

## Requirements

- **R1 Central logging.** Production services MUST send logs to the approved central logging platform.
- **R2 Structured logs.** Logs MUST be structured JSON and MUST carry a correlation identifier on every entry.
- **R3 Service level objectives.** Tier 1 and Tier 2 services MUST define service level objectives and alert on error budget burn.
- **R4.1 Retention.** Production application logs and security logs MUST be retained for 13 months (395 days) to support incident investigation and audit.
- **R4.2 Hot storage.** The most recent 30 days of logs MUST be searchable in hot storage.
- **R5 No secrets in logs.** Logs MUST NOT contain passwords, tokens, or keys.
- **R6 Tracing.** Services MUST propagate the W3C trace context.
- **R7 Dashboards and alerts.** Every production service MUST have a dashboard and an on-call alert route.
