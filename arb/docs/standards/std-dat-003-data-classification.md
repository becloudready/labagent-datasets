---
doc_id: STD-DAT-003
title: Data Classification and Handling Standard
doc_type: standard
version: 4.0
status: current
owner: Head of Data Architecture
effective_date: 2026-01-15
source_system: SharePoint
---

# STD-DAT-003 Data Classification and Handling Standard (version 4.0)

## Classes

Data is classified as Public, Internal, Confidential, or Restricted. Restricted data is customer proprietary network information, payment card data, government identifiers, and authentication secrets. Employee records and commercial contracts are Confidential.

## Requirements

- **R1 Classify.** Every data store MUST have a recorded classification owned by a named data owner.
- **R2 Restricted data protection.** Restricted data MUST be encrypted in transit and at rest and MUST only be accessed through audited, role-based access.
- **R3 Non-production.** Restricted data MUST NOT be used in non-production environments unless it is masked or replaced with synthetic data.
- **R4 Retention schedule.** Every data store MUST have a retention schedule approved by Legal and Privacy.
- **R5.1 Customer records.** Customer account records MUST be retained for 7 years after account closure and then deleted.
- **R5.2 Logs containing customer identifiers.** Application logs that contain customer identifiers (such as the phone number, account number, email address, or an identifier linked to an IP address) MUST be deleted or irreversibly pseudonymised within 90 days.
- **R6 Cross-border transfer.** Customer data MUST NOT leave the United States without written approval from Legal and Privacy.
- **R7 Backups.** Backups MUST follow the retention schedule of the data they contain and MUST NOT outlive it.
- **R8 Data subject requests.** Systems holding customer data MUST support search and deletion by customer identifier within 30 days of a verified request.
