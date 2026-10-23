---
doc_id: PROC-003
title: ARB Gate Definitions
doc_type: process
version: 2.2
status: current
owner: Chief Architect
effective_date: 2026-01-12
source_system: SharePoint
---

# ARB Gate Definitions

A gate is a point in the life of a solution where the ARB checks the design before the solution moves on. There are four gates. Not every solution passes every gate: the Front Door Guide says which apply.

## Gate 0: Intake

Entry: a requester has an idea and a sponsor. Evidence: Form ARB-F1 (Intake Request). Output: the Front Door assigns the applicable gates, forms, and tier within 2 business days. There is no ARB decision at Gate 0.

## Gate 1: Concept review

Purpose: confirm that the approach is sound before money is spent on detailed design. Evidence: Form ARB-F2 (Concept Brief) with business case, options considered, high level architecture, data classification, and known standards deviations. Outputs: Proceed, Rework, or Stop. Proceed means the team may start detailed design. It does not approve the design.

## Gate 2: Solution design review

Purpose: confirm that the detailed solution design meets the architecture standards. Evidence: Form ARB-F3 (Solution Architecture Pack) with architecture views, the standards compliance matrix, non-functional requirements, security and data protection design, resilience and recovery design, and any dispensation requests. Outputs: Approved, Approved with conditions, Deferred, or Not approved.

## Gate 3: Pre-production readiness

Purpose: confirm that what was built matches what was approved and that operations is ready. Evidence: Form ARB-F4 (Readiness Checklist) covering tested recovery, monitoring and alerting, runbooks, security testing results, and closure of every condition from Gate 2. Outputs: Go, Conditional go, or No-go. A solution with an open condition from Gate 2 cannot receive a Go.

## Re-entry

A Not approved or Deferred decision does not end the submission. The team fixes the issues and resubmits at the same gate. A resubmission keeps the original submission number with a suffix, for example SUB-2026-010 becomes SUB-2026-010-R1.
