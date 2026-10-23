---
doc_id: PROC-004
title: ARB Forms Catalog
doc_type: process
version: 2.3
status: current
owner: Front Door Coordinator
effective_date: 2026-02-02
source_system: SharePoint
---

# ARB Forms Catalog

All forms are completed in the ARB Submission Tracker. A submission is only marked Complete, and its service level clock only starts, when every mandatory field and attachment of the form is present.

## ARB-F1: Intake Request

Used at Gate 0 for every request. Completed by the requester. Mandatory fields: title, sponsor, business outcome, request type, expected data classes, hosting, target delivery date, and an estimate of total cost over the life of the solution. The Front Door Coordinator answers within 2 business days.

## ARB-F2: Concept Brief

Used at Gate 1. Completed by the lead architect of the project. Mandatory content: business case, at least two options with a recommendation, a context level architecture diagram, data classification, known deviations from the architecture standards, and the third-party risk assessment where a SaaS product is involved. The AI use review is attached for generative AI use cases.

## ARB-F3: Solution Architecture Pack

Used at Gate 2. Completed by the solution architect. Mandatory content: context, container, and deployment views, the standards compliance matrix, non-functional requirements, security and data protection design, resilience and recovery design with the stated recovery time and recovery point objectives, integration design, operational model, and dispensation requests (ARB-F5) for every deviation.

## ARB-F4: Readiness Checklist

Used at Gate 3. Completed by the delivery lead and the operations owner. Mandatory content: evidence that recovery was tested, monitoring and alerting in place, runbooks reviewed, penetration test or security assessment results, and a closure statement for every condition from Gate 2.

## ARB-F5: Dispensation Request

Used when a solution cannot meet a requirement of an architecture standard. Completed by the solution architect with the system owner. Mandatory content: the standard and requirement number, the reason compliance is not possible, the risk, compensating controls, a proposed expiry date, and a named owner. See the Dispensation Policy.

## ARB-F6: Appeal

Used to challenge an ARB decision. Completed by the sponsor. Mandatory content: the decision being appealed, the grounds, and new information not available to the ARB when it decided.
