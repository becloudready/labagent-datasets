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
    rows = list(csv.DictReader((ARB / "docs" / "registers" / "throughput-fy2026.csv").open()))
    h1 = [r for r in rows if r["decision_date"] and "2026-01-01" <= r["decision_date"] <= "2026-06-30"]
    t2 = [r for r in h1 if r["tier"] == "T2"]
    med = statistics.median(int(r["cycle_business_days"]) for r in t2)
    q = next(x for x in evalset if x["id"] == "num-01")
    assert q["expected_facts"] == [str(int(med)) if med == int(med) else str(med)]
    assert next(x for x in evalset if x["id"] == "num-02")["expected_facts"] == [str(sum(1 for r in t2 if r["sla_met"] == "No"))]


def test_tiers_follow_the_front_door_guide():
    rows = list(csv.DictReader((ARB / "docs" / "registers" / "throughput-fy2026.csv").open()))
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


def test_cycle_times_match_the_business_day_rule():
    rows = list(csv.DictReader((ARB / "docs" / "registers" / "throughput-fy2026.csv").open()))
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


def test_no_personal_or_real_customer_identifiers():
    banned = re.compile(r"AT&T|Collabera|Cognixia|Verizon|T-Mobile|Vodafone", re.I)
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for sub in ("process", "standards", "submissions", "dispensations", "minutes", "registers"):
        for p in (ARB / "docs" / sub).glob("*"):
            text = p.read_text()
            assert not banned.search(text), p.name
            assert not email.search(text), p.name


def test_standards_requirements_cited_by_submissions_exist():
    build.validate(build.all_records())
