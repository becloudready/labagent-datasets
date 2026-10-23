---
doc_id: PROC-001
title: Architecture Review Board Charter
doc_type: process
version: 2.0
status: current
owner: Chief Architect
effective_date: 2026-01-12
source_system: SharePoint
---

# Architecture Review Board Charter

## Purpose

The Architecture Review Board (ARB) makes sure that technology changes at Meridian Communications fit the enterprise architecture, meet the architecture standards, and carry risk that the business has knowingly accepted. The ARB does not own delivery. It owns the decision on whether a solution design is safe and consistent enough to proceed.

## Scope

The ARB reviews new systems, major changes to existing systems, software-as-a-service (SaaS) onboarding, generative AI use cases, decommissioning of systems that hold Confidential or Restricted data, and requests for dispensation from an architecture standard. Minor changes that do not alter data classification, external interfaces, or hosting are outside the ARB and are self-certified in the ARB Submission Tracker.

## Membership

- Chair: the Chief Architect. The Deputy Chair is the Head of Integration Architecture.
- Five domain architects: Security, Data, Infrastructure, Integration, and Application.
- Standing advisers without a vote: Legal and Privacy, Finance (FinOps), and the Front Door Coordinator.

## Quorum and decisions

A decision needs the Chair or Deputy Chair plus at least three of the five domain architects. Decisions are taken by consensus. If the board cannot reach consensus, the Chair decides and the dissenting view is recorded in the minutes. Each decision is one of: Approved, Approved with conditions, Deferred (more information needed), or Not approved. At Gate 1 the outcomes are named Proceed, Rework, and Stop.

## Meetings

The ARB working session is held every Tuesday from 10:00 to 11:30. Tier 2 and Tier 3 submissions are decided at the working session. Tier 1 submissions are decided asynchronously by two domain architects without a meeting. A full ARB meeting with the Architecture Council is held on the second Tuesday of each month and is used for Tier 3 submissions and for appeals. Minutes are published within 2 business days.

## Conditions

A condition attached to a decision has a named owner and a due date. A condition that is not met by its due date blocks the next gate for that submission. The Front Door Coordinator tracks conditions in the ARB Submission Tracker.

## Validity of decisions

An approval is valid for 12 months from the decision date. If the scope, the data classification, or the hosting changes materially during that time, the submission must come back to the ARB.

## Authority

The ARB reports to the Chief Technology Officer. The CTO may overrule an ARB decision only in writing, and the override is recorded in the governance log together with the risk acceptance.
