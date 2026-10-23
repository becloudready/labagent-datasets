#!/usr/bin/env python3
"""Try the ARB dataset against a local RAG setup (labagent[rag-local]: Chroma + MiniLM on CPU, no cloud account).

    pip install 'labagent[rag-local]'
    python3 arb/tools/try_local.py --version 2026.10 [--top-k 5] [--answers] [--only conf-01,nav-05]

Retrieval check: a question passes when at least one chunk of an expected document is in the top K.
--answers also asks the configured LLM (Groq / OpenAI / Anthropic key in the environment, else local Ollama, else a mock) and checks that the
expected facts appear in the answer (case-insensitive) and that questions with no answer are declined.
"""
import argparse
import gzip
import json
import re
import sys
from pathlib import Path

DECLINE = re.compile(r"(do not know|don't know|not (?:\w+ )?(?:in|covered|documented|stated|specified|mentioned|named|identified|listed|disclosed|given|available|provided|found)|cannot (?:find|answer)|can't (?:find|answer)|no (?:information|mention|record)|does not (?:\w+ )?(?:say|specify|contain|mention|include|name)|unable to)", re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="2026.10")
    ap.add_argument("--dist", default=str(Path(__file__).resolve().parent.parent / "dist"))
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--answers", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    from labagent.ai.rag import RAGLabClient

    dist = Path(a.dist)
    rows = [json.loads(l) for l in gzip.open(dist / f"arb-{a.version}.chunks.jsonl.gz", "rt")]
    questions = [json.loads(l) for l in open(dist / f"arb-{a.version}.eval.jsonl")]
    if a.only:
        keep = set(a.only.split(","))
        questions = [q for q in questions if q["id"] in keep]
    rag = RAGLabClient(vector_db="chroma")
    res = rag.ingest_chunks(rows)
    print(f"indexed {res.chunks} chunks from {res.documents} documents with {res.embedding_model} in {res.elapsed_ms / 1000:.0f}s\n")

    hits = total = 0
    fact_ok = fact_total = declined_ok = declined_total = 0
    by_cat = {}
    for q in questions:
        chunks = rag.retrieve(q["question"], top_k=a.top_k)
        got = [c.doc_id for c in chunks]
        line = f"{q['id']:8} {q['category']:10}"
        if q["expect_decline"]:
            line += f" (no answer expected) top score {chunks[0].similarity:.2f} from {got[0]}"
        else:
            ok = any(d in got for d in q["expected_docs"])
            hits += ok
            total += 1
            by_cat.setdefault(q["category"], []).append(ok)
            rank = next((i + 1 for i, d in enumerate(got) if d in q["expected_docs"]), None)
            line += f" {'HIT ' if ok else 'MISS'} rank={rank}  expected {q['expected_docs'][:2]}" + ("" if ok else f"  got {got[:3]}")
        if a.answers:
            r = rag.query(q["question"], top_k=a.top_k)
            ans = r.answer
            if q["expect_decline"]:
                declined_total += 1
                d_ok = bool(DECLINE.search(ans))
                declined_ok += d_ok
                line += f"\n         answer {'DECLINED' if d_ok else 'ANSWERED ANYWAY'}: {ans[:110]!r}"
            else:
                missing = [f for f in q["expected_facts"] if f.lower() not in ans.lower()]
                fact_total += 1
                fact_ok += not missing
                line += f"\n         facts {'ok' if not missing else 'missing ' + str(missing)} via {r.metrics.provider}"
        print(line)
    print(f"\nretrieval hit rate @ {a.top_k}: {hits}/{total} = {hits / total:.0%}" if total else "")
    for c, v in sorted(by_cat.items()):
        print(f"  {c:10} {sum(v)}/{len(v)}")
    if a.answers:
        print(f"answers with all expected facts: {fact_ok}/{fact_total}; declined when no answer exists: {declined_ok}/{declined_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
