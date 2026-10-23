---
doc_id: STD-INT-009
title: Integration and Messaging Standard
doc_type: standard
version: 1.5
status: current
owner: Head of Integration Architecture
effective_date: 2026-01-15
source_system: SharePoint
---

# STD-INT-009 Integration and Messaging Standard (version 1.5)

## Requirements

- **R1 Event driven first.** Integration between business domains SHOULD be event driven. Batch file integration needs a documented reason.
- **R2 Messaging platform.** Events MUST use the managed Kafka platform. Teams MUST NOT run their own brokers.
- **R3 No cross-domain database access.** A system MUST NOT read or write another domain's database directly.
- **R4 Schemas.** Every event MUST have a schema in the schema registry, and changes MUST be backward compatible.
- **R5 File transfer.** File transfer MUST use the managed file transfer service over SFTP.
- **R6 Idempotent consumers.** Consumers MUST tolerate duplicate delivery.
- **R7 Failure handling.** Consumers MUST use bounded retries and a dead-letter queue.
