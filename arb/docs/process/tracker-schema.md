---
doc_id: PROC-008
title: ARB Submission Tracker List Schema
doc_type: process
version: 1.1
status: current
owner: Front Door Coordinator
effective_date: 2026-02-02
source_system: SharePoint
---

# ARB Submission Tracker list schema

The ARB Submission Tracker is a SharePoint list. Each submission is one item, and the Front Door Coordinator updates it as the submission moves through the gates.

| Column | Type | Meaning |
|---|---|---|
| Title | Single line of text | Name of the project or change |
| SubmissionID | Single line of text | Number in the form SUB-2026-nnn. A resubmission adds -R1 |
| Requester | Single line of text | The sponsor |
| RequestType | Choice | One of the request types in the Front Door Guide |
| Tier | Choice | T1, T2, or T3 |
| CurrentGate | Choice | G0, G1, G2, or G3 |
| Status | Choice | In review, Approved, Approved with conditions, Deferred, Not approved, Withdrawn |
| CompleteDate | Date | The day the submission was marked Complete and the clock started |
| SLADueDate | Date | The date by which the decision is due |
| DecisionDate | Date | The day the decision was issued |
| OpenConditions | Number | Count of conditions not yet closed |

An automated agent that adds a new item must set Title, Requester, RequestType, Tier, and CurrentGate, and must set Status to In review. It must never set Status to an approval value.
