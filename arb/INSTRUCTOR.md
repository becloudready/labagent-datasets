# Instructor notes (not part of the corpus)

Keep this file out of any folder you upload for learners: it lists the planted traps and the expected answers.

## Planted conflicts (the Lab 3 "two standards disagree" exercise)

| Topic | Standard A | Standard B | What the ARB did |
|---|---|---|---|
| Logs that contain customer identifiers | STD-DAT-003 R5.2: delete or pseudonymise within **90 days** | STD-OBS-006 R4.1: retain production logs **13 months** | SUB-2026-005 ruling: 90 days for identifier logs plus a pseudonymised copy for 13 months, for that submission only. The correction to the standards is overdue (condition C2) |
| External API authentication | STD-API-004 R6: OAuth 2.0 with **mutual TLS bound** tokens | STD-SEC-002 R7: **bearer** tokens acceptable behind WAF profile W2, mutual TLS optional | SUB-2026-006 ruling: STD-API-004 is the more specific standard for API design, so it wins for new APIs. DISP-2026-004 covers 14 existing partners until 2026-12-31 |
| Tier 1 recovery time | STD-RES-005: **60 minutes** | STD-CLD-001 R9: **15 minutes**, active-active | DISP-2026-001 (SUB-2026-001) allows a warm standby. SUB-2026-010-R1 applied the same ruling |

A model that answers any of these with one confident number has hidden the conflict. The fix in Lab 3 is an instruction that requires contradictions to be surfaced.

## Governance drift hidden in email (the formats exercise)

Two replies to minutes emails change things that no register ever recorded. Real organisations drift like this.

| Reply | What it changes | Where the truth is | Where it is NOT |
|---|---|---|---|
| `MIN-2026-04-28-R1` (Legal, 2026-04-30) | Adds a requirement for SUB-2026-005: the key linking pseudonyms to customers must be destroyed at 90 days, or the 13 month copy is still personal data | Only in the email | The pack, the minutes, the governance log, and the conditions table |
| `MIN-2026-08-18-R1` (Chair, 2026-10-02) | Moves NetGraph condition C2 from 2026-11-15 to 2026-12-15 and warns that DISP-2026-005 still ends on 2026-11-30 | The email, which is the latest | The dispensation PDF, the register, and the tracker, which still say 2026-11-15 |

A system that answers from the pack or the register is wrong. A system that answers from the email alone misses the original context. The right answer combines them and flags the 15 day gap between the new due date and the end of the dispensation.

## Parsing notes

- The PDFs put the header and footer on every page. Default pypdf extraction keeps them inside chunks and splits every table row into one cell per line. Layout mode keeps rows on one line but needs the header and footer removed. `tools/extract.py` is a worked example.
- The superseded standard carries a diagonal SUPERSEDED watermark. Text extraction does not return it, but the metadata table on the page says `Status | Superseded`, and so does the chunk metadata.
- Bullet glyphs in the PDFs are emitted as a control character. The extractor converts them to `-`.
- The minutes emails quote the original in replies. A retriever that does not strip quoted lines will retrieve the same sentence twice.

## Other traps

- **Superseded standard.** STD-API-004 version 2.1 allowed partner API keys. Version 3.0 forbids them. The retriever may rank the old one first.
- **Expired dispensation.** DISP-2026-002 (EdgeSense) expired on 2026-09-30 and was not renewed. Dataset date is 2026-10-15.
- **Overdue condition.** SUB-2026-005 condition C2 (correct the standards conflict) was due 2026-07-31 and is still open.
- **Revoked dispensation.** DISP-2026-007 was revoked because the vendor delivered what it was waiting for, not because of a breach.
- **Questions with no answer.** The ARB approval budget limit (the Tier 1 cost limit of 50 thousand dollars is a tempting wrong answer), the name of the CTO delegate, and the name of the observability vendor are not documented anywhere.

## Aggregate questions (Lab 2, Analyst)

Baseline cycle time is defined in `PROC-009`: the median cycle time of decisions made from 1 January to 30 June 2026, per tier. The values are computed in the build and printed at the end of it. Plain retrieval is a poor way to answer these: a retrieved chunk holds 8 of the 76 rows. They show why the lab uses Analyst on the workbook.

## Rebuilding

`python3 arb/tools/build.py` is deterministic: the same inputs give byte-identical outputs. To change a fact, edit `arb/tools/submissions.py` (submissions, dispensations) or a Markdown file in `arb/docs/process` or `arb/docs/standards`, then rebuild. Tests: `python3 -m pytest arb/tests -q`.
