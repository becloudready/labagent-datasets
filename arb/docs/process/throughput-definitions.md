---
doc_id: PROC-009
title: Throughput Workbook Definitions
doc_type: process
version: 1.0
status: current
owner: Front Door Coordinator
effective_date: 2026-02-02
source_system: SharePoint
---

# Throughput workbook definitions

The throughput workbook has one row per gate decision.

- **Cycle time** is the number of business days from the day the submission is marked Complete to the decision date, minus the business days the clock was paused. Weekends and company holidays are not counted.
- **Baseline cycle time** is the median cycle time of the decisions made between 1 January 2026 and 30 June 2026 (the first half of the year), reported per tier.
- **Service level met** is Yes when the cycle time is no more than the service level for the tier: 3 business days for Tier 1, 10 for Tier 2, and 20 for Tier 3.
- Rows without a decision date are still in review and are excluded from the baseline.
