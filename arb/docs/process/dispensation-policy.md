---
doc_id: PROC-006
title: Dispensation Policy
doc_type: policy
version: 1.4
status: current
owner: Chief Architect
effective_date: 2026-01-12
source_system: SharePoint
---

# Dispensation Policy

A dispensation is a time-limited permission to deviate from a requirement of an architecture standard. It is not a waiver of the standard. The standard continues to apply to everyone else, and to the requester again when the dispensation ends.

## When a dispensation can be granted

The ARB may grant a dispensation when full compliance is not technically or commercially feasible within the delivery timeline, the risk is understood and acceptable, and compensating controls are in place. A dispensation cannot be granted for a requirement marked as a legal or regulatory obligation.

## What every dispensation must have

1. The standard and requirement number being deviated from.
2. The reason compliance is not possible.
3. Compensating controls that reduce the risk.
4. One or more conditions, each with a named owner and a due date.
5. An expiry date, and a named owner accountable for it.

## Duration and renewal

The maximum duration of a dispensation is 12 months. A dispensation may be renewed once, for up to 6 months, if the owner shows progress against the conditions. After that the system must comply or the matter goes to the CTO. A renewal request (ARB-F5) must be filed at least 20 business days before the expiry date, because the dispensation service level is 15 business days.

## Expiry

When a dispensation expires, the standard applies again. A system that still deviates is non-compliant, and the owner must either comply, renew in time, or take the matter to the CTO. The Front Door Coordinator reports expired dispensations to the Chair every month.

## Revocation

The Chair may revoke a dispensation when a condition is breached or when the risk changes. Revocation is recorded in the governance log with the reason.

## Register

All dispensations are recorded in the Dispensation Register with their conditions, owner, expiry date, and status: Active, Expired, or Revoked.
