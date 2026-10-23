---
doc_id: STD-AI-007
title: AI and Generative AI Use Standard
doc_type: standard
version: 1.3
status: current
owner: Head of Data Architecture
effective_date: 2026-04-01
source_system: SharePoint
---

# STD-AI-007 AI and Generative AI Use Standard (version 1.3)

## Requirements

- **R1 Registry.** Every AI use case MUST be entered in the AI use case registry before build starts.
- **R2 Approved providers.** Models MUST be consumed only from the approved providers: Azure OpenAI Service and Amazon Bedrock, inside the Meridian tenancy.
- **R3 Restricted data.** Restricted data MUST NOT be sent to a model that runs outside the Meridian tenancy.
- **R4 Human oversight.** Decisions that affect a customer MUST have human review before they take effect.
- **R5 Customer-facing GenAI.** A customer-facing generative AI capability MUST pass Gate 2 as a Tier 3 submission and MUST be red-team tested before launch.
- **R6 Prompt and response logging.** Prompts and responses MUST be logged with personal data redacted and retained for 30 days.
- **R7 Evidence.** The submission MUST include a model description, the evaluation method, and the results against a written test set that includes questions with no answer in the sources.
- **R8 Retrieval and permissions.** A retrieval-augmented system MUST only retrieve content the signed-in user is allowed to read. Retrieval MUST be trimmed by the source system permissions.
