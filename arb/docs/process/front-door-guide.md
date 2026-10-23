---
doc_id: PROC-002
title: ARB Front Door Guide
doc_type: process
version: 3.1
status: current
owner: Front Door Coordinator
effective_date: 2026-02-02
source_system: SharePoint
---

# ARB Front Door Guide

## What the Front Door does

Every request starts at the Front Door. The requester submits Form ARB-F1 (Intake Request). The Front Door Coordinator triages it within 2 business days and tells the requester which gate applies, which form to complete next, and which service level (tier) the request is in. The decision on the tier is the Coordinator's, and a requester can ask the Chair to review it.

## Which gate, form, and tier applies

| Request type | Gate and form | Tier |
|---|---|---|
| New system or platform | Gate 1 with ARB-F2, then Gate 2 with ARB-F3, then Gate 3 with ARB-F4 | Tier 2, or Tier 3 if a Tier 3 trigger applies |
| Major change to an existing system (changes data classification, adds an external interface, or moves hosting) | Gate 2 with ARB-F3, then Gate 3 with ARB-F4 | Tier 2, or Tier 3 if a Tier 3 trigger applies |
| SaaS onboarding handling only Public or Internal data | Gate 1 with ARB-F2 and the third-party risk assessment | Tier 1 |
| SaaS onboarding handling Confidential data | Gate 1 with ARB-F2 and the third-party risk assessment, then Gate 2 with ARB-F3 | Tier 2 |
| SaaS onboarding handling Restricted data | Gate 1 with ARB-F2 and the third-party risk assessment, then Gate 2 with ARB-F3 | Tier 3 |
| Generative AI use case, internal users only | Gate 1 with ARB-F2 and an AI use review under STD-AI-007 | Tier 2 |
| Generative AI use case that is customer facing | Gate 1 with ARB-F2 and an AI use review under STD-AI-007, then Gate 2 with ARB-F3 | Tier 3 |
| Decommissioning a system that holds Confidential or Restricted data | Gate 3 with ARB-F4 | Tier 1 |
| Exception to an architecture standard | Dispensation process with ARB-F5 | Dispensation service level (15 business days) |
| Appeal of an ARB decision | ARB-F6 | Appeal service level (10 business days) |
| Minor change that does not alter data classification, external interfaces, or hosting | No ARB gate. Self-certify in the ARB Submission Tracker | Not applicable |

## Tier 3 triggers

A request is Tier 3 when any of these is true: total cost over 2 million US dollars over the life of the solution, Restricted data is stored or processed, the solution is a customer-facing generative AI capability, or a new strategic vendor platform is introduced.

## Tier 1 criteria

A request can be Tier 1 only when it uses approved patterns, introduces no new Confidential or Restricted data, adds no new external connectivity, and costs under 50 thousand US dollars.

## What the Front Door cannot do

The Front Door does not approve designs and does not grant dispensations. It does not decide budgets or funding. Questions about funding limits go to Finance.
