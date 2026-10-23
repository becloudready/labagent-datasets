---
doc_id: MIN-2026-04-28
title: ARB minutes 2026-04-28
doc_type: minutes
version: 1.0
status: current
owner: Dev Patel
effective_date: 2026-04-28
source_system: SharePoint
---


# ARB working session minutes, 2026-04-28

## Attendance

Present: Priya Raman (Chair, Chief Architect); Tomas Berg (Security Architect); Aiko Tanaka (Data Architect); Marcus Oyelaran (Infrastructure Architect); Lena Fischer (Integration Architect, Deputy Chair); Samir Haddad (Application Architect); Dev Patel (Front Door Coordinator).

Absent: none. Quorum (Chair or Deputy plus three domain architects): met.

## Items decided

### SUB-2026-005 Customer360 lakehouse (G2, Tier 3 (Strategic))

Decision: **Approved with conditions**.

The submission exposed a conflict: STD-DAT-003 R5.2 requires identifier logs to be gone in 90 days, while STD-OBS-006 R4.1 requires 13 months for production logs. Following the Appeals and Escalation process the Chair ruled for this submission only that identifier logs are kept 90 days and a pseudonymised copy is kept 13 months. The ruling does not change either standard.

Conditions:

- C1: Implement pseudonymisation of customer identifiers before logs are shipped. Owner Lead Data Engineer, due 2026-07-31.
- C2: Ask the owners of STD-DAT-003 and STD-OBS-006 to publish a correction that resolves the conflict. Owner Chief Data Officer, due 2026-07-31.

## Next session

Tuesday at 10:00. Minutes are published within 2 business days.
