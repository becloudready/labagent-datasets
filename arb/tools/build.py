#!/usr/bin/env python3
"""Build the ARB dataset: render derived documents, validate everything, chunk, and write the release files.

    python3 arb/tools/build.py --version 2026.10 [--out arb/dist]

Reads : arb/docs/process, arb/docs/standards (authored), arb/public (fetched), arb/tools/submissions.py (authored data)
Writes: arb/docs/submissions, dispensations, minutes, registers  (rendered, committed so they can be reviewed and edited by hand)
        arb/dist/arb-<version>.{chunks.jsonl.gz, eval.jsonl, corpus.zip, manifest.json}, SHA256SUMS

Deterministic: same inputs give byte-identical outputs. Evaluation answers that depend on numbers or dates are COMPUTED from the data.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import random
import re
import statistics
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402
import render_eml  # noqa: E402
import render_pdf  # noqa: E402
import submissions as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PUBLIC = ROOT / "public"
HOLIDAYS = {dt.date.fromisoformat(d) for d in ("2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07", "2026-10-12")}
SLA_DAYS = {"T1": 3, "T2": 10, "T3": 20}
TIER_NAME = {"T1": "Tier 1 (Fast-track)", "T2": "Tier 2 (Standard)", "T3": "Tier 3 (Strategic)"}
AS_OF = dt.date.fromisoformat(S.AS_OF)
CONTENT_LICENSE = "CC BY 4.0 (fictional training content authored by BeCloudReady)"
MAX_CHUNK = 1400


# ---------------------------------------------------------------- dates
def D(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def is_bday(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS


def bdays_between(a: dt.date, b: dt.date) -> int:
    """Business days after `a` up to and including `b` (so same day = 0)."""
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        if is_bday(d):
            n += 1
    return n


def add_bdays(a: dt.date, n: int) -> dt.date:
    d = a
    while n > 0:
        d += dt.timedelta(days=1)
        if is_bday(d):
            n -= 1
    return d


def next_tuesday(d: dt.date) -> dt.date:
    while d.weekday() != 1 or d in HOLIDAYS:
        d += dt.timedelta(days=1)
    return d


# ---------------------------------------------------------------- records
def full_records() -> List[Dict[str, Any]]:
    """One record per gate decision of the authored submissions."""
    out = []
    for s in S.SUBMISSIONS:
        for gate, complete, decided, paused, outcome in s["gates"]:
            out.append(dict(submission=s["id"], name=s["name"], tier=s["tier"], gate=gate, request_type=s["request_type"], sponsor=s["sponsor"],
                            complete=D(complete), decided=D(decided) if decided else None, paused=paused, outcome=outcome, full=True))
    return out


NAMES = {
    "Major change to an existing system": ["Rotate TLS certificates tooling", "Internal wiki search upgrade", "Call recording archive", "Developer portal refresh", "SIM provisioning API v2",
                                           "Number portability gateway", "Secrets vault upgrade", "Roaming partner settlement", "Customer notification service", "Config management database cleanup",
                                           "Order management upgrade", "Backup platform consolidation"],
    "New system or platform": ["Retail store Wi-Fi analytics", "Field service scheduling", "Fraud rules engine", "Network capacity planner", "Spectrum licence tracker", "Inventory forecasting"],
    "SaaS onboarding": ["Incident status page", "Expense reporting SaaS", "Data catalogue SaaS", "Training platform SaaS", "Meeting notes SaaS", "Design collaboration SaaS", "Signature SaaS"],
    "Generative AI use case (internal users only)": ["Churn prediction model", "Enterprise chat bot for IT help", "Voicemail transcription", "Contract summary assistant"],
    "Decommissioning a system that holds Confidential or Restricted data": ["Legacy billing archive decommission", "Old data mart decommission", "Retired provisioning system"],
}
TYPE_WEIGHTS = [("Major change to an existing system", 34), ("New system or platform", 20), ("SaaS onboarding", 30),
                ("Generative AI use case (internal users only)", 8), ("Decommissioning a system that holds Confidential or Restricted data", 8)]
GATE_CHOICES = {"New system or platform": ["G1", "G2", "G3"], "Major change to an existing system": ["G2", "G3"], "SaaS onboarding": ["G1"],
                "Generative AI use case (internal users only)": ["G1"], "Decommissioning a system that holds Confidential or Restricted data": ["G3"]}
CYCLE_TARGETS = {"T1": [1, 2, 2, 2, 3, 3, 3, 3, 4, 5], "T2": [6, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 13, 16], "T3": list(range(14, 25))}


def tier_for(rtype: str, rng: random.Random) -> str:
    """Follows the Front Door Guide, so the generated records never contradict the process documents."""
    r = rng.random()
    if rtype == "Decommissioning a system that holds Confidential or Restricted data":
        return "T1"
    if rtype == "Generative AI use case (internal users only)":
        return "T2"
    if rtype == "SaaS onboarding":
        return "T1" if r < 0.6 else "T2" if r < 0.9 else "T3"
    if rtype == "Major change to an existing system":
        return "T2" if r < 0.85 else "T3"
    return "T2" if r < 0.75 else "T3"


def generated_records(n: int = 57) -> List[Dict[str, Any]]:
    """Smaller submissions with no full pack. Deterministic: seeded RNG, fixed lists."""
    rng = random.Random(2026)
    sponsors = ["VP Network Technology", "VP Customer Care", "VP Platform Engineering", "CHRO", "VP Wholesale", "CFO Office", "VP Digital Commerce", "Chief Data Officer"]
    types = [t for t, _ in TYPE_WEIGHTS]
    weights = [w for _, w in TYPE_WEIGHTS]
    used: Dict[str, int] = {}
    out = []
    for _ in range(n):
        rtype = rng.choices(types, weights)[0]
        names = NAMES[rtype]
        k = used.get(rtype, 0)
        used[rtype] = k + 1
        title = names[k % len(names)] + ("" if k < len(names) else f" phase {k // len(names) + 1}")
        tier = tier_for(rtype, rng)
        complete = D("2026-01-12") + dt.timedelta(days=rng.randrange(0, 270))
        while not is_bday(complete):
            complete += dt.timedelta(days=1)
        target = rng.choice(CYCLE_TARGETS[tier]) if tier != "T3" else rng.choice(CYCLE_TARGETS["T3"])
        paused = rng.choice([0, 0, 0, 1, 2, 3]) if tier != "T1" else 0
        decided = add_bdays(complete, target + paused)
        if tier != "T1":
            decided = next_tuesday(decided)
        roll = rng.random()
        outcome = ("Approved" if roll < 0.70 else "Approved with conditions" if roll < 0.92 else "Deferred" if roll < 0.96 else "Not approved") if tier != "T1" else \
                  ("Approved" if roll < 0.90 else "Approved with conditions" if roll < 0.98 else "Not approved")
        if decided > AS_OF:
            decided, outcome = None, "In review"
        out.append(dict(name=title, tier=tier, gate=rng.choice(GATE_CHOICES[rtype]), request_type=rtype, sponsor=rng.choice(sponsors),
                        complete=complete, decided=decided, paused=paused, outcome=outcome, full=False))
    out.sort(key=lambda r: r["complete"])
    for i, r in enumerate(out):
        r["submission"] = f"SUB-2026-{15 + i:03d}"
    return out


def all_records() -> List[Dict[str, Any]]:
    recs = full_records() + generated_records()
    for r in recs:
        r["sla"] = SLA_DAYS[r["tier"]]
        if r["decided"]:
            r["cycle"] = max(1, bdays_between(r["complete"], r["decided"]) - r["paused"])
            r["sla_met"] = r["cycle"] <= r["sla"]
        else:
            r["cycle"], r["sla_met"] = None, None
    recs.sort(key=lambda r: (r["decided"] or AS_OF + dt.timedelta(days=1), r["submission"], r["gate"]))
    return recs


def dispensation_status(d: Dict[str, Any]) -> str:
    if d.get("revoked_on"):
        return "Revoked"
    return "Expired" if D(d["expiry"]) < AS_OF else "Active"


# ---------------------------------------------------------------- standards index (for validation)
def standards_index() -> Dict[str, set]:
    idx: Dict[str, set] = {}
    for p in sorted((DOCS / "standards").glob("*.md")):
        fm, body = parse(p.read_text())
        if fm.get("status") != "current":
            continue
        idx[fm["doc_id"]] = set(re.findall(r"\*\*(R\d+(?:\.\d+)?)\b", body))
    return idx


def parse(text: str) -> Tuple[Dict[str, str], str]:
    m = re.match(r"---\n(.*?)\n---\n\n?(.*)", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm, m.group(2)


def validate(recs) -> None:
    std = standards_index()
    problems = []
    for s in S.SUBMISSIONS:
        for req, _status, _note in s["compliance"]:
            sid, rn = req.rsplit(" ", 1)
            if sid not in std or rn not in std[sid]:
                problems.append(f"{s['id']}: unknown requirement {req}")
        for gate, complete, decided, _p, _o in s["gates"]:
            if decided and s["tier"] in ("T2", "T3") and D(decided).weekday() != 1:
                problems.append(f"{s['id']}: {decided} is not a Tuesday")
            if not is_bday(D(complete)):
                problems.append(f"{s['id']}: complete date {complete} is not a business day")
        for d in s["dispensations"]:
            if d not in {x["id"] for x in S.DISPENSATIONS}:
                problems.append(f"{s['id']}: unknown dispensation {d}")
    for d in S.DISPENSATIONS:
        if d["standard"] not in std or d["requirement"] not in std[d["standard"]]:
            problems.append(f"{d['id']}: unknown requirement {d['standard']} {d['requirement']}")
        if d["submission"] not in {s["id"] for s in S.SUBMISSIONS}:
            problems.append(f"{d['id']}: unknown submission")
        if (D(d["expiry"]) - D(d["granted"])).days > 366:
            problems.append(f"{d['id']}: longer than the 12 month maximum")
    if problems:
        raise SystemExit("validation failed:\n  " + "\n  ".join(problems))


# ---------------------------------------------------------------- rendering
def front(doc_id: str, title: str, doc_type: str, extra: Optional[Dict[str, str]] = None) -> str:
    base = {"doc_id": doc_id, "title": title, "doc_type": doc_type, "version": "1.0", "status": "current", "owner": "Front Door Coordinator",
            "effective_date": S.AS_OF, "source_system": "SharePoint"}
    base.update(extra or {})
    return "---\n" + "\n".join(f"{k}: {v}" for k, v in base.items()) + "\n---\n\n"


def render_submission(s: Dict[str, Any]) -> str:
    final = [g for g in s["gates"] if g[2]][-1] if any(g[2] for g in s["gates"]) else s["gates"][-1]
    lines = [front(s["id"], f"{s['id']} {s['name']}", "submission", {"owner": s["lead"], "effective_date": final[2] or final[1], "tier": s["tier"],
                                                                        "request_type": s["request_type"], "outcome": final[4]}),
             f"# {s['id']} {s['name']}", "", "## Summary", "", s["summary"], "",
             f"Sponsor: {s['sponsor']}. Lead architect: {s['lead']}. Request type: {s['request_type']}. {TIER_NAME[s['tier']]}. "
             f"Data classification: {s['data_class']}. Service tier: {s['service_tier']}. Estimated cost: {s['cost_musd']} million US dollars.", "",
             "## Architecture", ""] + [f"- {a}" for a in s["architecture"]] + ["", "## Non-functional requirements", "", s["nfr"], "",
             "## Standards compliance matrix", "", "| Requirement | Status | Note |", "|---|---|---|"] + \
            [f"| {r} | {st} | {n} |" for r, st, n in s["compliance"]] + ["", "## Options considered", ""] + \
            [f"- **{n}.** {d}" for n, d in s["options"]] + ["", "## Decisions"]
    for gate, complete, decided, paused, outcome in s["gates"]:
        lines += ["", f"### {gate}: {outcome}", "",
                  f"Complete: {complete}. " + (f"Decided: {decided}. Paused: {paused} business days." if decided else "Decision pending.")]
    lines += ["", "## Discussion and rationale", "", s["discussion"], "", "## Conditions", ""]
    if s["conditions"]:
        lines += ["| Condition | Text | Owner | Due | Status |", "|---|---|---|---|---|"] + [f"| {c['id']} | {c['text']} | {c['owner']} | {c['due']} | {c['status']} |" for c in s["conditions"]]
    else:
        lines += ["No conditions."]
    if s["dispensations"]:
        lines += ["", "## Dispensations", ""] + [f"- {d}" for d in s["dispensations"]]
    return "\n".join(lines) + "\n"


def render_dispensation(d: Dict[str, Any]) -> str:
    st = dispensation_status(d)
    sub = next(x for x in S.SUBMISSIONS if x["id"] == d["submission"])
    lines = [front(d["id"], f"{d['id']} Dispensation for {sub['name']}", "dispensation", {"owner": d["owner"], "effective_date": d["granted"], "status": st}),
             f"# {d['id']} Dispensation (ARB-F5)", "", "## Request", "",
             f"Submission: {d['submission']} {sub['name']}. Standard and requirement: {d['standard']} {d['requirement']}. Accountable owner: {d['owner']}.", "",
             f"Deviation: {d['deviation']}", "", f"Reason: {d['rationale']}", "", f"Compensating controls: {d['compensating']}", "",
             "## Decision", "", f"Granted: {d['granted']}. Expiry: {d['expiry']}. Status as of {S.AS_OF}: {st}."]
    if d.get("revoked_on"):
        lines += ["", f"Revoked on {d['revoked_on']}. {d['revoked_reason']}"]
    if st == "Expired":
        lines += ["", f"This dispensation expired on {d['expiry']}. No renewal request (ARB-F5) was filed. The standard {d['standard']} {d['requirement']} applies again and the system is non-compliant until it complies or a renewal is granted."]
    lines += ["", "## Conditions", "", "| Condition | Owner | Due | Status |", "|---|---|---|---|"] + [f"| {t} | {o} | {due} | {s} |" for t, o, due, s in d["conditions"]]
    return "\n".join(lines) + "\n"


def log_rows(recs) -> List[Dict[str, Any]]:
    rows = []
    n = 0
    full = {s["id"]: s for s in S.SUBMISSIONS}
    for r in sorted((x for x in recs if x["decided"]), key=lambda x: (x["decided"], x["submission"])):
        n += 1
        s = full.get(r["submission"])
        conds, disp, notes = "", "", ""
        if s and r["gate"] == s["gates"][-1][0] and r["decided"] == D(s["gates"][-1][2] or "1900-01-01"):
            conds = "; ".join(f"{c['id']} {c['text']} (owner {c['owner']}, due {c['due']})" for c in s["conditions"])
            disp = ", ".join(s["dispensations"])
            notes = s["discussion"]
        elif s:
            notes = s["discussion"] if r["outcome"] == "Deferred" else ""
        rows.append(dict(decision_id=f"DEC-2026-{n:03d}", decision_date=r["decided"].isoformat(), submission_id=r["submission"], submission_name=r["name"], gate=r["gate"],
                         tier=r["tier"], outcome=r["outcome"], decided_by="Async: two domain architects" if r["tier"] == "T1" else "ARB working session",
                         conditions=conds, dispensation_id=disp, notes=notes))
    return rows


def minutes_inputs(date: dt.date, recs) -> Tuple[List[str], Optional[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(date.toordinal())
    absent = rng.choice([None, "sec", "data", "infra", "app"])
    present = [S.PEOPLE[k] for k in ("chair", "sec", "data", "infra", "integ", "app") if k != absent] + [S.PEOPLE["front"]]
    byid = {s["id"]: s for s in S.SUBMISSIONS}
    items, others = [], []
    for r in recs:
        if r["decided"] != date or r["tier"] == "T1":
            continue
        base = dict(id=r["submission"], name=r["name"], gate=r["gate"], tier_name=TIER_NAME[r["tier"]], outcome=r["outcome"])
        if r["full"]:
            sub = byid[r["submission"]]
            last = sub["gates"][-1]
            final = r["gate"] == last[0] and r["decided"] == D(last[2] or "1900-01-01")
            items.append(dict(base, discussion=sub["discussion"], conditions=sub["conditions"] if final else [],
                              dispensations=sub["dispensations"] if final and r["outcome"].startswith("Approved") else []))
        else:
            others.append(base)
    return present, absent, items, others


def minutes_emails(date: dt.date, recs) -> List[Tuple[str, bytes, Dict[str, str]]]:
    """(doc_id, .eml bytes, info) for the minutes email and any follow-up replies. The email is sent one business day after the session."""
    present, absent, items, others = minutes_inputs(date, recs)
    sent_day = add_bdays(date, 1)
    sent = dt.datetime(sent_day.year, sent_day.month, sent_day.day, 16, random.Random(date.toordinal() + 1).randint(5, 55), tzinfo=render_eml._tz(sent_day))
    msg = render_eml.minutes_message(date, sent, present, absent, items, others)
    out = [(f"MIN-{date.isoformat()}", render_eml.to_bytes(msg), dict(date=date.isoformat(), kind="minutes"))]
    for f in S.FOLLOWUPS:
        if f["minutes"] == date.isoformat():
            out.append((f"MIN-{date.isoformat()}-{f['suffix']}", render_eml.to_bytes(render_eml.reply_message(msg, f)), dict(date=f["sent"][:10], kind="reply")))
    return out


def csv_text(rows: List[Dict[str, Any]], cols: List[str]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
    return buf.getvalue()


def throughput_rows(recs) -> List[Dict[str, Any]]:
    rows = []
    for r in sorted(recs, key=lambda x: (x["complete"], x["submission"], x["gate"])):
        rows.append(dict(submission_id=r["submission"], name=r["name"], tier=r["tier"], gate=r["gate"], request_type=r["request_type"], complete_date=r["complete"].isoformat(),
                         decision_date=r["decided"].isoformat() if r["decided"] else "", paused_business_days=r["paused"], cycle_business_days=r["cycle"] if r["cycle"] is not None else "",
                         sla_business_days=r["sla"], sla_met=("Yes" if r["sla_met"] else "No") if r["sla_met"] is not None else "", outcome=r["outcome"]))
    return rows


def tracker_rows(recs) -> List[Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for r in sorted(recs, key=lambda x: (x["complete"], x["gate"])):
        latest[r["submission"]] = r
    full = {s["id"]: s for s in S.SUBMISSIONS}
    rows = []
    for sid, r in sorted(latest.items()):
        s = full.get(sid)
        open_c = sum(1 for c in s["conditions"] if c["status"] == "Open") if s else 0
        rows.append(dict(Title=r["name"], SubmissionID=sid, Requester=r["sponsor"], RequestType=r["request_type"], Tier=r["tier"], CurrentGate=r["gate"],
                         Status=r["outcome"], CompleteDate=r["complete"].isoformat(), SLADueDate=add_bdays(r["complete"], r["sla"] + r["paused"]).isoformat(),
                         DecisionDate=r["decided"].isoformat() if r["decided"] else "", OpenConditions=open_c))
    return rows


TRACKER_SCHEMA = """---
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
"""

THROUGHPUT_DEFS = """---
doc_id: PROC-009
title: Throughput Workbook Definitions
doc_type: process
version: 1.0
status: current
owner: Front Door Coordinator
effective_date: 2026-02-02
source_system: SharePoint
---

# Throughput workbook definitions

The throughput workbook has one row per gate decision.

- **Cycle time** is the number of business days from the day the submission is marked Complete to the decision date, minus the business days the clock was paused. Weekends and company holidays are not counted.
- **Baseline cycle time** is the median cycle time of the decisions made between 1 January 2026 and 30 June 2026 (the first half of the year), reported per tier.
- **Service level met** is Yes when the cycle time is no more than the service level for the tier: 3 business days for Tier 1, 10 for Tier 2, and 20 for Tier 3.
- Rows without a decision date are still in review and are excluded from the baseline.
"""


# ---------------------------------------------------------------- chunking
def split_sections(body: str) -> List[Tuple[str, str]]:
    """(heading, text) pairs. The text keeps its sub-headings so a merged chunk still reads naturally."""
    parts, cur_title, cur = [], "Overview", []
    for line in body.splitlines():
        m = re.match(r"^(#{1,3}) (.*)", line)
        if m and len(m.group(1)) == 2:
            if "".join(cur).strip():
                parts.append((cur_title, "\n".join(cur).strip()))
            cur_title, cur = m.group(2).strip(), []
        elif m and len(m.group(1)) == 1:
            continue                                   # the document title is already in the chunk prefix
        else:
            cur.append(line)                           # level 3 headings stay inside their section
    if "".join(cur).strip():
        parts.append((cur_title, "\n".join(cur).strip()))
    return parts


def pack_lines(text: str, limit: int) -> List[str]:
    """Split one long block (a list or a table) on line boundaries. A table keeps its two header lines in every piece."""
    lines = text.split("\n")
    header = lines[:2] if len(lines) > 2 and lines[0].startswith("|") and lines[1].startswith("|") else []
    out, cur = [], list(header)
    for ln in lines[len(header):]:
        if len("\n".join(cur + [ln])) > limit and len(cur) > len(header):
            out.append("\n".join(cur))
            cur = list(header)
        cur.append(ln)
    if len(cur) > len(header):
        out.append("\n".join(cur))
    return out


def pack(text: str, limit: int = MAX_CHUNK) -> List[str]:
    """Pieces of at most about `limit` characters, cut on blank lines, then on lines for long lists and tables."""
    if len(text) <= limit:
        return [text]
    out, cur = [], ""
    for block in re.split(r"\n\s*\n", text):
        pieces = pack_lines(block, limit) if len(block) > limit else [block]
        for piece in pieces:
            if cur and len(cur) + len(piece) + 2 > limit:
                out.append(cur)
                cur = ""
            cur = (cur + "\n\n" + piece).strip() if cur else piece
    if cur:
        out.append(cur)
    return out


def doc_chunks(path: Path, source_path: str, public: bool) -> List[Dict[str, Any]]:
    fm, body = parse(path.read_text())
    doc_id = fm["doc_id"]
    meta_base = {k: fm[k] for k in ("doc_type", "title", "version", "status", "owner", "effective_date", "source_system", "tier", "outcome", "request_type") if k in fm}
    meta_base.update(doc_id=doc_id, source_path=source_path)
    if public:
        meta_base.update(doc_type="reference", source_system="Public", status="current", license=fm["license"], url=fm["source_url"], attribution=fm["attribution"], retrieved=fm["retrieved"])
    else:
        meta_base["license"] = CONTENT_LICENSE
    title = fm.get("title", doc_id)
    # greedy: put consecutive sections into one chunk until it would exceed the limit, so tiny sections are not stranded as stubs
    groups: List[List[Tuple[str, str]]] = []
    cur: List[Tuple[str, str]] = []
    size = 0
    for section, text in split_sections(body):
        for piece in pack(text):
            if cur and size + len(piece) > MAX_CHUNK:
                groups.append(cur)
                cur, size = [], 0
            cur.append((section, piece))
            size += len(piece) + 2
    if cur:
        groups.append(cur)
    chunks = []
    for n, g in enumerate(groups, 1):
        first = g[0][0]
        sections = [first] + [s for s, _ in g[1:] if s != first]
        content = "\n\n".join((f"## {s}\n{t}" if i and s != g[i - 1][0] else t) for i, (s, t) in enumerate(g))
        chunks.append(dict(id=f"{doc_id}-{n}", doc_id=doc_id, title=f"{title}, {first}", content=f"{title} > {first}\n{content}",
                           meta={**meta_base, "section": " / ".join(sections)}))
    return chunks


def table_chunks(doc_id: str, title: str, doc_type: str, rows: List[Dict[str, Any]], cols: List[str], per: int, source_path: str) -> List[Dict[str, Any]]:
    out = []
    for i in range(0, len(rows), per):
        grp = rows[i:i + per]
        text = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" + "\n".join("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in grp)
        out.append(dict(id=f"{doc_id}-{i // per + 1}", doc_id=doc_id, title=f"{title}, rows {i + 1} to {i + len(grp)}", content=f"{title}\n{text}",
                        meta=dict(doc_id=doc_id, doc_type=doc_type, title=title, section=f"rows {i + 1}-{i + len(grp)}", source_system="SharePoint", status="current",
                                  source_path=source_path, source_format="csv", license=CONTENT_LICENSE)))
    return out


def group_blocks(blocks: List[Tuple[int, str, str]]) -> List[List[Tuple[int, str, str]]]:
    """Greedy grouping of (page, section, text) blocks into chunks of about MAX_CHUNK characters. Long blocks are cut on line boundaries first."""
    groups, cur, size = [], [], 0
    for pg, sec, text in blocks:
        for piece in (pack_lines(text, MAX_CHUNK) if len(text) > MAX_CHUNK else [text]):
            if cur and size + len(piece) > MAX_CHUNK:
                groups.append(cur)
                cur, size = [], 0
            cur.append((pg, sec, piece))
            size += len(piece) + 2
    if cur:
        groups.append(cur)
    return groups


def pdf_file_chunks(path: Path, rel: str, fm: Dict[str, str], naive: bool = False) -> List[Dict[str, Any]]:
    """Chunks from the PDF itself. Section names come from the PDF's bookmarks, page numbers from the extraction."""
    pages = extract.pdf_pages(path, naive=naive)
    titles = {t for _, t in extract.pdf_outline(path)}
    blocks, section = [], "Overview"
    for pg, text in pages:
        for block in re.split(r"\n\s*\n", text):
            first = block.strip().splitlines()[0].strip() if block.strip() else ""
            if first in titles:
                section = first
            if block.strip():
                blocks.append((pg, section, block))
    doc_id, title = fm["doc_id"], fm.get("title", fm["doc_id"])
    meta_base = {k: fm[k] for k in ("doc_type", "title", "version", "status", "owner", "effective_date", "source_system", "tier", "outcome", "request_type") if k in fm}
    meta_base.update(doc_id=doc_id, source_path=rel, source_format="pdf", license=CONTENT_LICENSE)
    out = []
    for n, g in enumerate(group_blocks(blocks), 1):
        first = g[0][1]
        secs = list(dict.fromkeys(sec for _, sec, _ in g))
        out.append(dict(id=f"{doc_id}-{n}", doc_id=doc_id, title=f"{title}, {first}", content=f"{title} > {first}\n" + "\n\n".join(t for _, _, t in g),
                        meta={**meta_base, "section": " / ".join(secs), "page_start": g[0][0], "page_end": g[-1][0]}))
    return out


def eml_file_chunks(path: Path, rel: str, doc_id: str, info: Dict[str, str]) -> List[Dict[str, Any]]:
    headers, body = extract.eml_text(path)
    head = "\n".join(f"{k}: {headers[k]}" for k in ("From", "To", "Date", "Subject") if k in headers)
    pieces = pack(head + "\n\n" + body)
    subj = headers.get("Subject", doc_id)
    base = dict(doc_id=doc_id, doc_type="minutes" if info["kind"] == "minutes" else "email", title=subj, source_system="Outlook", status="current",
                effective_date=info["date"], source_path=rel, source_format="eml", sender=headers.get("From", ""), subject=subj, license=CONTENT_LICENSE)
    if "In-Reply-To" in headers:
        base["in_reply_to"] = headers["In-Reply-To"]
    return [dict(id=f"{doc_id}-{n}", doc_id=doc_id, title=subj, content=f"{piece}", meta={**base, "section": "email body" if n > 1 else "headers and opening"})
            for n, piece in enumerate(pieces, 1)]


def file_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def pdf_filename(fm: Dict[str, str]) -> str:
    t, d = fm["doc_type"], fm["doc_id"]
    if t == "standard":
        return f"{d}_{file_slug(fm['title'])}_v{fm['version']}.pdf"
    if t == "submission":
        return f"{d}_{file_slug(fm['title'].split(' ', 1)[1])}_ARB-F3.pdf"
    if t == "dispensation":
        return f"{d}_ARB-F5.pdf"
    return f"{file_slug(fm['title'])}_v{fm['version']}.pdf"


def workbook(sheets: Dict[str, Tuple[List[str], List[List[Any]]]]) -> Optional[bytes]:
    """An Excel workbook from {sheet name: (columns, rows)}. Reproducible (fixed timestamps). None when openpyxl is not installed."""
    try:
        from openpyxl import Workbook
    except ImportError:
        return None
    wb = Workbook()
    wb.remove(wb.active)
    for name, (cols, rows) in sheets.items():
        ws = wb.create_sheet(name)
        ws.append(cols)
        for r in rows:
            ws.append(r)
        ws.freeze_panes = "A2"
    wb.properties.creator = "BeCloudReady"
    wb.properties.created = wb.properties.modified = dt.datetime(2026, 10, 15)
    buf = io.BytesIO()
    wb.save(buf)
    return normalise_zip(buf.getvalue())


def table_workbook(rows: List[Dict[str, Any]], cols: List[str], name: str, definitions: str = "") -> Optional[bytes]:
    numeric = {"paused_business_days", "cycle_business_days", "sla_business_days", "OpenConditions"}
    data = [[(int(r[c]) if c in numeric and r.get(c, "") != "" else r.get(c, "")) for c in cols] for r in rows]
    sheets = {name: (cols, data)}
    if definitions:
        lines = [re.sub(r"^[#\-\s*]+", "", l).replace("**", "") for l in re.sub(r"^---.*?---\n", "", definitions, flags=re.S).strip().splitlines() if l.strip()]
        sheets["Definitions"] = (["Definitions"], [[l] for l in lines])
    return workbook(sheets)


def normalise_zip(data: bytes) -> bytes:
    """openpyxl stamps every file inside the .xlsx with the current time. Rewrite it with a fixed time so the build is reproducible."""
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for name in sorted(src.namelist()):
            body = src.read(name)
            if name == "docProps/core.xml":                # openpyxl rewrites the modified time on every save
                body = re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:)", rb"\g<1>2026-10-15T00:00:00Z\g<2>", body)
            dst.writestr(zipfile.ZipInfo(name, date_time=(2026, 10, 15, 0, 0, 0)), body)
    return out.getvalue()


# ---------------------------------------------------------------- evaluation set
def build_eval(recs, disp_rows, throughput) -> List[Dict[str, Any]]:
    h1 = [r for r in recs if r["decided"] and D("2026-01-01") <= r["decided"] <= D("2026-06-30")]
    def med(t): return statistics.median([r["cycle"] for r in h1 if r["tier"] == t])
    t2h1 = [r for r in h1 if r["tier"] == "T2"]
    t2_breach = sum(1 for r in t2h1 if not r["sla_met"])
    longest = max(("T1", "T2", "T3"), key=med)
    open_overdue = [(s["id"], c["id"]) for s in S.SUBMISSIONS for c in s["conditions"] if c["status"] == "Open" and D(c["due"]) < AS_OF]
    open_overdue += [(d["id"], t[:30]) for d in S.DISPENSATIONS if not d.get("revoked_on") for t, _o, due, st in d["conditions"] if st == "Open" and D(due) < AS_OF]
    expire_2026 = sorted(d["id"] for d in S.DISPENSATIONS if dispensation_status(d) == "Active" and D(d["expiry"]).year == 2026)
    qs = [
        ("nav-01", "navigator", "We want to onboard a SaaS survey tool that only handles Internal data. Which gate, form and service level apply?", ["PROC-002", "PROC-004", "PROC-005"], ["Gate 1", "ARB-F2", "Tier 1", "3 business days"], False),
        ("nav-02", "navigator", "We are making a major change to the rating engine of an existing billing system that stores Restricted data. Which gates, forms and service level apply?", ["PROC-002", "PROC-005"], ["Gate 2", "ARB-F3", "Gate 3", "ARB-F4", "Tier 3", "20 business days"], False),
        ("nav-03", "navigator", "A partner API cannot meet the mutual TLS requirement. What process do we follow and how long does it take?", ["PROC-006", "PROC-002", "PROC-005"], ["ARB-F5", "15 business days"], False),
        ("nav-04", "navigator", "We plan a customer-facing generative AI assistant. Which gates apply and which tier is it?", ["PROC-002", "STD-AI-007"], ["Gate 1", "Gate 2", "Tier 3"], False),
        ("nav-05", "navigator", "What is the largest project budget the ARB is allowed to approve?", [], [], True),
        ("nav-06", "navigator", "Who is the current CTO delegate who approves expedited dispensations?", [], [], True),
        ("conf-01", "conflict", "How long must production application logs that contain customer identifiers be kept?", ["STD-DAT-003", "STD-OBS-006"], ["90 days", "13 months"], False),
        ("conf-02", "conflict", "Do external APIs need access tokens bound with mutual TLS, or are plain bearer tokens enough?", ["STD-API-004", "STD-SEC-002"], ["STD-API-004", "STD-SEC-002"], False),
        ("conf-03", "conflict", "What recovery time must a Tier 1 workload meet?", ["STD-RES-005", "STD-CLD-001"], ["60 minutes", "15 minutes"], False),
        ("ver-01", "version", "Can we give a wholesale partner an API key to call our external API?", ["STD-API-004"], ["API keys"], False),
        ("tmp-01", "temporal", "Is the EdgeSense log retention dispensation still valid today?", ["DISP-2026-002"], ["expired", "2026-09-30"], False),
        ("tmp-02", "temporal", "Which active dispensations expire before the end of 2026?", ["REG-DISPENSATIONS", "DISP-2026-004", "DISP-2026-005"], expire_2026, False),
        ("hop-01", "multi-hop", "What conditions were attached to the dispensation for the PartnerHub API gateway?", ["DISP-2026-004", "SUB-2026-006"], ["wave 1", "wave 2", "wave 3", "2026-11-30"], False),
        ("hop-02", "multi-hop", "Why was the first PaymentsEdge submission not approved?", ["SUB-2026-010"], ["tokenis", "4 hour"], False),
        ("hop-03", "multi-hop", "Which conditions are overdue as of 15 October 2026?", ["SUB-2026-005"], [f"{open_overdue[0][0]}"] if open_overdue else [], False),
        ("hop-04", "multi-hop", "How did the ARB resolve the conflict between the API standard and the identity standard for PartnerHub?", ["SUB-2026-006"], ["STD-API-004", "more specific"], False),
        ("hop-05", "multi-hop", "What did the ARB decide about log retention for the Customer360 lakehouse?", ["SUB-2026-005"], ["90 days", "pseudonymised", "13 months"], False),
        ("hop-06", "multi-hop", "Which submissions were not approved or deferred, and why?", ["SUB-2026-010", "SUB-2026-011", "REG-GOVLOG"], ["SUB-2026-010", "SUB-2026-011"], False),
        ("num-01", "aggregate", "What is the baseline cycle time for Tier 2 submissions in the first half of 2026?", ["PROC-009", "PROC-005"], [str(int(med("T2")) if med("T2") == int(med("T2")) else med("T2"))], False),
        ("num-02", "aggregate", "How many Tier 2 decisions in the first half of 2026 missed the 10 business day service level?", ["PROC-009"], [str(t2_breach)], False),
        ("num-03", "aggregate", "Which tier has the longest median cycle time in the first half of 2026?", ["PROC-009"], [{"T1": "Tier 1", "T2": "Tier 2", "T3": "Tier 3"}[longest]], False),
        ("pub-01", "public", "What does the Google Cloud Well-Architected Framework say about designing for reliability?", ["PUB-gcp-af-reliability"], ["reliab"], False),
        ("pub-02", "public", "What does the UK Technology Code of Practice say about using cloud first?", ["PUB-uk-tcop-use-cloud-first"], ["cloud"], False),
        ("pub-03", "public", "What are the abstractions of the C4 model?", ["PUB-c4-abstractions"], ["container", "component"], False),
        ("pub-04", "public", "How do I record an architecture decision with the MADR template?", ["PUB-madr-template"], ["Context", "Decision"], False),
        ("proc-01", "process", "How long is an ARB approval valid and when must a submission come back?", ["PROC-001"], ["12 months"], False),
        ("proc-02", "process", "Can the CTO overrule an ARB decision?", ["PROC-001", "PROC-007"], ["in writing"], False),
        ("proc-03", "process", "What is the quorum for an ARB decision?", ["PROC-001"], ["three of the five"], False),
        ("proc-04", "process", "What must a retrieval-augmented AI system do about user permissions?", ["STD-AI-007", "SUB-2026-014"], ["permission"], False),
        ("mail-01", "email", "What additional requirement did Legal and Privacy put on the pseudonymised logs for the Customer360 lakehouse?", ["MIN-2026-04-28-R1"], ["key", "destroyed", "90 days"], False),
        ("mail-02", "email", "What is the current due date for the NetGraph masking condition, and does the dispensation still cover it?", ["MIN-2026-08-18-R1", "DISP-2026-005"], ["2026-12-15", "2026-11-30"], False),
        ("dec-01", "decline", "What is the name of the vendor selected for the observability platform?", [], [], True),
    ]
    traps = {"nav-05": "The Tier 1 criteria mention 50 thousand US dollars, which is a fast-track eligibility limit, not an approval limit.",
             "nav-06": "The Service Levels document mentions a CTO delegate but the corpus never names who it is.",
             "dec-01": "SUB-2026-012 mentions 'the vendor' and a 1.4 million dollar cost estimate, but never names the vendor.",
             "conf-01": "A good answer surfaces BOTH standards and the conflict, and mentions that the Chair ruled for SUB-2026-005 only.",
             "conf-02": "A good answer surfaces the conflict between STD-API-004 R6 and STD-SEC-002 R7 and that STD-API-004 was ruled more specific for PartnerHub.",
             "conf-03": "STD-RES-005 says 60 minutes, STD-CLD-001 R9 says 15 minutes. A confident single number hides the conflict.",
             "ver-01": "STD-API-004 version 2.1 (superseded) allowed API keys for partners; version 3.0 does not. The superseded document must not win.",
             "mail-01": "The condition exists ONLY in a reply email. The submission pack, the minutes, and the governance log do not mention it.",
             "mail-02": "The due date was moved by email on 2026-10-02 and never reached the register or tracker, which still say 2026-11-15. The dispensation ends 2026-11-30, 15 days before the new date.",
             "tmp-01": "The dispensation text says granted until 2026-09-30; the dataset date is 2026-10-15, so it has expired and no renewal was filed."}
    return [dict(id=i, category=c, question=q, expected_docs=d, expected_facts=f, expect_decline=dc, **({"trap": traps[i]} if i in traps else {})) for i, c, q, d, f, dc in qs]


# ---------------------------------------------------------------- output
def gz(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, compresslevel=9) as f:
        f.write(data)
    return buf.getvalue()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_if_changed(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="2026.10")
    ap.add_argument("--out", default=str(ROOT / "dist"))
    a = ap.parse_args()

    recs = all_records()
    validate(recs)

    # derived documents that stay as reviewable Markdown (the PDFs below are rendered from these)
    for s_ in S.SUBMISSIONS:
        write_if_changed(DOCS / "submissions" / f"{s_['id']}.md", render_submission(s_))
    for d in S.DISPENSATIONS:
        write_if_changed(DOCS / "dispensations" / f"{d['id']}.md", render_dispensation(d))
    write_if_changed(DOCS / "process" / "tracker-schema.md", TRACKER_SCHEMA)
    write_if_changed(DOCS / "process" / "throughput-definitions.md", THROUGHPUT_DEFS)
    rows = log_rows(recs)
    log_cols = ["decision_id", "decision_date", "submission_id", "submission_name", "gate", "tier", "outcome", "decided_by", "conditions", "dispensation_id", "notes"]
    thr = throughput_rows(recs)
    thr_cols = list(thr[0].keys())
    trk = tracker_rows(recs)
    trk_cols = list(trk[0].keys())
    disp_rows = [dict(dispensation_id=d["id"], submission_id=d["submission"], standard=d["standard"], requirement=d["requirement"], status=dispensation_status(d),
                      granted=d["granted"], expiry=d["expiry"], owner=d["owner"], deviation=d["deviation"],
                      conditions="; ".join(f"{t} (owner {o}, due {due}, {st})" for t, o, due, st in d["conditions"])) for d in S.DISPENSATIONS]
    disp_cols = list(disp_rows[0].keys())
    registers = {"governance-log": (rows, log_cols, "Governance log"), "throughput-fy2026": (thr, thr_cols, "Throughput"),
                 "arb-submission-tracker": (trk, trk_cols, "ARB Submission Tracker"), "dispensation-register": (disp_rows, disp_cols, "Dispensation Register")}
    for name, (r, c, _t) in registers.items():
        write_if_changed(DOCS / "registers" / f"{name}.csv", csv_text(r, c))

    # ---- render the corpus as the files an organisation would really hold
    out = Path(a.out)
    corpus = out / "corpus"
    if corpus.exists():
        import shutil
        shutil.rmtree(corpus)
    files: List[Dict[str, Any]] = []
    for sub in ("process", "standards", "submissions", "dispensations"):
        for p in sorted((DOCS / sub).glob("*.md")):
            fm, body = parse(p.read_text())
            target = corpus / sub / pdf_filename(fm)
            render_pdf.render_pdf(target, fm, body)
            files.append(dict(kind="pdf", path=target, rel=f"corpus/{sub}/{target.name}", fm=fm))
    for dte in sorted({r["decided"] for r in recs if r["full"] and r["decided"] and r["tier"] != "T1"}):
        for doc_id, data, info in minutes_emails(dte, recs):
            target = corpus / "minutes" / f"{doc_id}.eml"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files.append(dict(kind="eml", path=target, rel=f"corpus/minutes/{target.name}", doc_id=doc_id, info=info))
    for name, (r, c, tab) in registers.items():
        (corpus / "registers").mkdir(parents=True, exist_ok=True)
        (corpus / "registers" / f"{name}.csv").write_text(csv_text(r, c))
        xl = table_workbook(r, c, tab, THROUGHPUT_DEFS if name == "throughput-fy2026" else "")
        if xl:
            (corpus / "registers" / f"{name}.xlsx").write_bytes(xl)
    (corpus / "public").mkdir(parents=True, exist_ok=True)
    for p in sorted(PUBLIC.glob("*.md")):
        (corpus / "public" / p.name).write_bytes(p.read_bytes())

    # ---- chunks come from EXTRACTING those files (not from the Markdown sources)
    def build_chunks(naive: bool) -> List[Dict[str, Any]]:
        ch: List[Dict[str, Any]] = []
        for f in files:
            if f["kind"] == "pdf":
                ch += pdf_file_chunks(f["path"], f["rel"], f["fm"], naive=naive)
            else:
                ch += eml_file_chunks(f["path"], f["rel"], f["doc_id"], f["info"])
        for p in sorted(PUBLIC.glob("*.md")):
            ch += doc_chunks(p, f"corpus/public/{p.name}", public=True)
        ch += table_chunks("REG-DISPENSATIONS", "Dispensation Register", "register", disp_rows, ["dispensation_id", "submission_id", "standard", "requirement", "status", "granted", "expiry", "owner"], 8, "corpus/registers/dispensation-register.csv")
        ch += table_chunks("REG-GOVLOG", "Governance Log", "register", rows, ["decision_id", "decision_date", "submission_id", "submission_name", "gate", "tier", "outcome"], 8, "corpus/registers/governance-log.csv")
        ch += table_chunks("REG-THROUGHPUT", "Throughput Workbook FY2026", "register", thr, ["submission_id", "tier", "gate", "complete_date", "decision_date", "cycle_business_days", "sla_met", "outcome"], 8, "corpus/registers/throughput-fy2026.csv")
        ch += table_chunks("REG-TRACKER", "ARB Submission Tracker", "register", trk, ["SubmissionID", "Title", "Tier", "CurrentGate", "Status", "DecisionDate", "OpenConditions"], 8, "corpus/registers/arb-submission-tracker.csv")
        return ch

    chunks = build_chunks(naive=False)
    naive_chunks = build_chunks(naive=True)
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids)), "duplicate chunk ids"

    ev = build_eval(recs, disp_rows, thr)
    known = {c["doc_id"] for c in chunks}
    for q in ev:
        for d in q["expected_docs"]:
            if d not in known:
                raise SystemExit(f"eval {q['id']}: unknown expected doc {d}")

    v = a.version
    out.mkdir(parents=True, exist_ok=True)
    jl = lambda cs: gz(("\n".join(json.dumps(c, ensure_ascii=False, sort_keys=True) for c in cs) + "\n").encode())
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(x for x in corpus.rglob("*") if x.is_file()):
            z.writestr(zipfile.ZipInfo(str(p.relative_to(out)), date_time=(2026, 10, 15, 0, 0, 0)), p.read_bytes())
    released = {f"arb-{v}.chunks.jsonl.gz": jl(chunks), f"arb-{v}.chunks-naive-pdf.jsonl.gz": jl(naive_chunks),
                f"arb-{v}.eval.jsonl": ("\n".join(json.dumps(q, ensure_ascii=False, sort_keys=True) for q in ev) + "\n").encode(), f"arb-{v}.corpus.zip": zbuf.getvalue()}
    kinds: Dict[str, int] = {}
    for c in chunks:
        kinds[c["meta"]["doc_type"]] = kinds.get(c["meta"]["doc_type"], 0) + 1
    formats: Dict[str, int] = {}
    for p in corpus.rglob("*"):
        if p.is_file():
            formats[p.suffix.lstrip(".")] = formats.get(p.suffix.lstrip("."), 0) + 1
    manifest = dict(name="arb", version=v, as_of=S.AS_OF, chunks=len(chunks), documents=len({c["doc_id"] for c in chunks}), questions=len(ev),
                    chunks_by_type=dict(sorted(kinds.items())), corpus_files_by_format=dict(sorted(formats.items())),
                    files={n: dict(bytes=len(b), sha256=sha(b)) for n, b in released.items()})
    man = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    released[f"arb-{v}.manifest.json"] = man
    for n, b in released.items():
        (out / n).write_bytes(b)
    (out / "SHA256SUMS").write_text("".join(f"{sha(b)}  {n}\n" for n, b in sorted(released.items())))
    print(json.dumps({k: manifest[k] for k in ("version", "chunks", "documents", "questions", "chunks_by_type", "corpus_files_by_format")}, indent=2))
    t2 = [r["cycle"] for r in recs if r["decided"] and r["tier"] == "T2" and D("2026-01-01") <= r["decided"] <= D("2026-06-30")]
    print(f"baseline cycle time, Tier 2, H1 2026 (median business days): {statistics.median(t2)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
