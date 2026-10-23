---
doc_id: STD-CLD-001
title: Cloud Architecture Standard
doc_type: standard
version: 3.2
status: current
owner: Head of Infrastructure Architecture
effective_date: 2026-02-01
source_system: SharePoint
---

# STD-CLD-001 Cloud Architecture Standard (version 3.2)

This standard sets the rules for hosting workloads in public cloud at Meridian Communications.

## Requirements

- **R1 Approved platforms.** Workloads MUST run on Amazon Web Services, which is the primary platform, or on Microsoft Azure where the workload is tied to Microsoft 365 or the analytics platform. Any other cloud platform needs a dispensation.
- **R2 Landing zone.** Workloads MUST be deployed in accounts or subscriptions created from the Meridian landing zone. Workloads MUST NOT run in personal, sandbox, or test accounts.
- **R3 Infrastructure as code.** All production infrastructure MUST be provisioned through infrastructure as code with a reviewed pipeline. Manual changes in the console MUST NOT be made in production.
- **R4 Tagging.** Every resource MUST carry the tags owner, cost-centre, data-class, service-tier, and environment.
- **R5 Regions.** Workloads that store US customer data MUST run only in us-east-1 and us-west-2.
- **R6 Network exposure.** Compute resources MUST NOT have public IP addresses. Internet traffic MUST enter through the approved edge services with a web application firewall.
- **R7 Encryption.** Data at rest classified Confidential or Restricted MUST be encrypted with customer-managed keys.
- **R8 Containers.** Container images MUST come from the approved base image catalogue and MUST be scanned before deployment.
- **R9 Tier 1 availability.** Tier 1 workloads MUST be deployed active-active across two regions and MUST be able to recover within 15 minutes.
- **R10 Cost governance.** A workload forecast to cost more than 20 thousand US dollars per month MUST have a FinOps review before go-live.

## Notes

Service tiers (Tier 1 to Tier 4) are defined by the business impact analysis. See the Resilience and Disaster Recovery Standard for recovery objectives per tier.
