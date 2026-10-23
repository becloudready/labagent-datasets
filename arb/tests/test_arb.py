"""Consistency tests for the ARB dataset. Run: python3 -m pytest arb/tests -q"""
import csv
import datetime as dt
import gzip
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

ARB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ARB / "tools"))
import build  # noqa: E402
import submissions as S  # noqa: E402


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    subprocess.run([sys.executable, str(ARB / "tools" / "build.py"), "--version", "t", "--out", str(out)], check=True, capture_output=True)
    return out


@pytest.fixture(scope="module")
def chunks(dist):
    return [json.loads(l) for l in gzip.open(dist / "arb-t.chunks.jsonl.gz", "rt")]


@pytest.fixture(scope="module")
def evalset(dist):
    return [json.loads(l) for l in open(dist / "arb-t.eval.jsonl")]


def test_build_is_deterministic(dist, tmp_path):
    import time
    time.sleep(2.1)          # a build that embeds the current time (it did, inside the .xlsx) differs after a second or more
    subprocess.run([sys.executable, str(ARB / "tools" / "build.py"), "--version", "t", "--out", str(tmp_path)], check=True, capture_output=True)
    assert (dist / "SHA256SUMS").read_text() == (tmp_path / "SHA256SUMS").read_text()


def test_checksums_match_the_files(dist):
    for line in (dist / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ")
        assert build.sha((dist / name).read_bytes()) == digest


def test_chunk_ids_unique_and_sizes_sane(chunks):
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids))
    sizes = [len(c["content"]) for c in chunks]
    assert max(sizes) < 1800 and sum(1 for x in sizes if x < 150) <= 3
    for c in chunks:
        assert c["doc_id"] and c["meta"]["doc_type"] and c["meta"]["license"] and c["content"].strip()


def test_every_chunk_has_attribution_or_a_content_licence(chunks):
    for c in chunks:
        m = c["meta"]
        if m["doc_type"] == "reference":
            assert m["url"].startswith("https://") and m["attribution"] and m["retrieved"]
            assert any(k in m["license"] for k in ("CC BY 4.0", "Creative Commons Attribution 4.0", "Open Government Licence v3.0", "MIT"))
        else:
            assert "fictional" in m["license"]


def test_only_redistributable_public_sources(chunks):
    """Allowed: CC BY 4.0, OGL v3.0, MIT or CC0. Anything else must stay link-only (see the data card)."""
    ok = ("Creative Commons Attribution 4.0", "Open Government Licence v3.0", "MIT OR CC0-1.0")
    for lic in {c["meta"]["license"] for c in chunks if c["meta"]["doc_type"] == "reference"}:
        assert any(lic.startswith(o) for o in ok), lic


def test_eval_references_exist_and_declines_have_no_sources(chunks, evalset):
    docs = {c["doc_id"] for c in chunks}
    assert len(evalset) >= 25 and len({q["id"] for q in evalset}) == len(evalset)
    for q in evalset:
        if q["expect_decline"]:
            assert q["expected_docs"] == [] and q["expected_facts"] == []
        else:
            assert q["expected_docs"] and set(q["expected_docs"]) <= docs
    assert sum(q["expect_decline"] for q in evalset) >= 3
    assert {q["category"] for q in evalset} >= {"navigator", "conflict", "temporal", "multi-hop", "aggregate", "public", "decline"}


def test_numeric_answers_are_computed_from_the_data(dist, evalset):
    rows = list(csv.DictReader((ARB / "build" / "registers" / "throughput-fy2026.csv").open()))
    h1 = [r for r in rows if r["decision_date"] and "2026-01-01" <= r["decision_date"] <= "2026-06-30"]
    t2 = [r for r in h1 if r["tier"] == "T2"]
    med = statistics.median(int(r["cycle_business_days"]) for r in t2)
    q = next(x for x in evalset if x["id"] == "num-01")
    assert q["expected_facts"] == [str(int(med)) if med == int(med) else str(med)]
    assert next(x for x in evalset if x["id"] == "num-02")["expected_facts"] == [str(sum(1 for r in t2 if r["sla_met"] == "No"))]


def test_tiers_follow_the_front_door_guide(dist):
    rows = list(csv.DictReader((ARB / "build" / "registers" / "throughput-fy2026.csv").open()))
    for r in rows:
        t, rt = r["tier"], r["request_type"]
        if "Decommissioning" in rt:
            assert t == "T1"
        if t == "T1":
            assert rt.startswith(("SaaS", "Decommissioning"))
        if rt.startswith("Generative AI") and "internal" in rt:
            assert t == "T2"
        if r["decision_date"] and t in ("T2", "T3"):
            assert dt.date.fromisoformat(r["decision_date"]).weekday() == 1, r["submission_id"]


def test_cycle_times_match_the_business_day_rule(dist):
    rows = list(csv.DictReader((ARB / "build" / "registers" / "throughput-fy2026.csv").open()))
    for r in rows:
        if r["decision_date"]:
            got = build.bdays_between(build.D(r["complete_date"]), build.D(r["decision_date"])) - int(r["paused_business_days"])
            assert int(r["cycle_business_days"]) == max(1, got)
            assert (r["sla_met"] == "Yes") == (int(r["cycle_business_days"]) <= int(r["sla_business_days"]))


def test_dispensations_follow_the_policy():
    for d in S.DISPENSATIONS:
        assert (dt.date.fromisoformat(d["expiry"]) - dt.date.fromisoformat(d["granted"])).days <= 366
        assert d["conditions"]
    status = {d["id"]: build.dispensation_status(d) for d in S.DISPENSATIONS}
    assert status["DISP-2026-002"] == "Expired" and status["DISP-2026-007"] == "Revoked" and status["DISP-2026-004"] == "Active"


def test_three_planted_conflicts_and_one_superseded_standard_exist():
    std = {p.name: p.read_text() for p in (ARB / "docs" / "standards").glob("*.md")}
    all_std = "\n".join(std.values())
    assert "within 90 days" in all_std and "13 months (395 days)" in all_std                       # log retention
    assert "mutual TLS (RFC 8705)" in all_std and "mutual TLS) is OPTIONAL" in all_std             # API authentication
    assert "within 15 minutes" in all_std and "| Tier 1 | Mission critical" in all_std            # Tier 1 recovery
    assert sum("status: superseded" in t for t in std.values()) == 1


def test_no_personal_or_real_customer_identifiers(chunks, dist):
    banned = re.compile(r"AT&T|Collabera|Cognixia|Verizon|T-Mobile|Vodafone", re.I)
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for p in [*(ARB / "docs").glob("*/*.md"), *(ARB / "build").glob("*/*")]:
        text = p.read_text()
        assert not banned.search(text), p.name
        assert not email.search(text), p.name
    for c in chunks:                                  # the only addresses anywhere are on the reserved .example domain
        if c["meta"]["doc_type"] == "reference":
            continue
        assert not banned.search(c["content"]), c["id"]
        for addr in email.findall(c["content"]):
            assert addr.endswith("@meridian.example"), (c["id"], addr)


def test_standards_requirements_cited_by_submissions_exist():
    build.validate(build.all_records())


# ---- formats: the corpus must be the files an organisation would really hold
def test_corpus_holds_real_formats(dist):
    corpus = dist / "corpus"
    assert len(list(corpus.glob("standards/*.pdf"))) == 10 and len(list(corpus.glob("submissions/*.pdf"))) == 15
    assert len(list(corpus.glob("dispensations/*.pdf"))) == 7 and len(list(corpus.glob("process/*.pdf"))) == 9
    assert len(list(corpus.glob("minutes/*.eml"))) >= 15
    assert list(corpus.glob("minutes/*.md")) == [] and list(corpus.glob("standards/*.md")) == []
    assert list(corpus.glob("registers/*.xlsx"))
    for p in corpus.glob("**/*.pdf"):
        assert p.read_bytes()[:5] == b"%PDF-"


def test_minutes_are_valid_threaded_emails(dist):
    import email
    from email import policy
    first = email.message_from_bytes((dist / "corpus/minutes/MIN-2026-04-28.eml").read_bytes(), policy=policy.default)
    reply = email.message_from_bytes((dist / "corpus/minutes/MIN-2026-04-28-R1.eml").read_bytes(), policy=policy.default)
    assert first["Subject"].startswith("ARB working session minutes") and first["Message-ID"] and first["Date"]
    assert reply["In-Reply-To"] == first["Message-ID"] and reply["Subject"] == "Re: " + first["Subject"]
    assert "destroyed" in reply.get_body(("plain",)).get_content()
    assert reply["Date"] and email.utils.parsedate_to_datetime(reply["Date"]) > email.utils.parsedate_to_datetime(first["Date"])


def test_pdf_extraction_keeps_table_rows_and_drops_page_furniture(chunks):
    sub6 = [c for c in chunks if c["doc_id"] == "SUB-2026-006"]
    text = "\n".join(c["content"] for c in sub6)
    assert "STD-API-004 R6 | Conflict | Requires mutual TLS bound tokens." in text      # a table row survives as one line
    assert "Uncontrolled when printed" not in text and "Page 1 of" not in text           # header and footer are removed
    assert all(c["meta"]["source_format"] == "pdf" and c["meta"]["page_start"] >= 1 for c in sub6)
    assert not any(ord(ch) < 32 and ch not in "\n\t" or ord(ch) == 127 for c in chunks for ch in c["content"])


def test_naive_extraction_is_measurably_worse(dist, chunks):
    import gzip as gz
    naive = [json.loads(l) for l in gz.open(dist / "arb-t.chunks-naive-pdf.jsonl.gz", "rt")]
    row = "STD-API-004 R6 | Conflict | Requires mutual TLS bound tokens."
    assert row not in "\n".join(c["content"] for c in naive if c["doc_id"] == "SUB-2026-006")
    assert any("Uncontrolled when printed" in c["content"] for c in naive)               # furniture stays in naive chunks


def test_the_superseded_standard_is_marked_in_the_pdf_itself(chunks):
    old = [c for c in chunks if c["doc_id"] == "STD-API-004-V2.1"]
    assert old and all(c["meta"]["status"] == "superseded" for c in old)
    assert "Superseded" in old[0]["content"] and "replaced by version 3.0" in old[0]["content"]


def test_follow_up_emails_change_things_the_registers_do_not_know(chunks, dist):
    reply2 = " ".join(c["content"] for c in chunks if c["doc_id"] == "MIN-2026-08-18-R1")
    assert "2026-12-15" in reply2 and "DISP-2026-005" in reply2
    register = (ARB / "build" / "registers" / "dispensation-register.csv").read_text()
    assert "2026-11-15" in register and "2026-12-15" not in register                      # the drift is deliberate and documented
    legal = " ".join(c["content"] for c in chunks if c["doc_id"] == "MIN-2026-04-28-R1")
    assert "destroyed" in legal
    assert "destroyed" not in (ARB / "build" / "submissions" / "SUB-2026-005.md").read_text()


def test_eval_has_email_questions(evalset):
    assert {"mail-01", "mail-02"} <= {q["id"] for q in evalset} and any(q["category"] == "email" for q in evalset)


def test_generated_files_are_not_committed():
    """The Markdown intermediates and CSVs are rebuilt from submissions.py: committing them only invites drift."""
    tracked = subprocess.run(["git", "ls-files", "arb/build", "arb/dist"], cwd=ARB.parent, capture_output=True, text=True).stdout.split()
    assert tracked == []
    ignored = (ARB.parent / ".gitignore").read_text()
    assert "arb/build/" in ignored and "arb/dist/" in ignored
    assert not list((ARB / "docs").glob("submissions")) and not list((ARB / "docs").glob("registers"))


def test_corpus_registers_ship_as_excel_only(dist):
    names = sorted(p.name for p in (dist / "corpus" / "registers").iterdir())
    assert names == ["arb-submission-tracker.xlsx", "dispensation-register.xlsx", "governance-log.xlsx", "throughput-fy2026.xlsx"]
