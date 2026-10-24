# labagent-datasets: checksummed datasets for RAG labs and workshops

> Real-world datasets for **retrieval-augmented generation (RAG)** labs: **SEC 10-K filings** and an **architecture review board (ARB)** corpus in PDF, email and Excel. Every released file has a SHA-256 checksum. Built for [labagent](https://github.com/becloudready/labagent), usable with any vector database.

**Related:** [labagent](https://github.com/becloudready/labagent) (the lab CLI) | [DB Agent](https://github.com/db-agent/db-agent) (text-to-SQL agent) | [BeCloudReady workshops](https://github.com/becloudready/workshops)

## Datasets

| Dataset | What it is | Formats | Size | Status |
|---|---|---|---|---|
| [`sec-10k`](sec-10k/README.md) | 1,880 section-split passages from 10 annual reports (Apple, Chevron, JPMorgan, Pfizer, Walmart; two years each) | JSONL (gzip) | 0.5 MB | Released: `2026.10` |
| [`arb`](arb/README.md) | 82 documents of a fictional telecom's architecture review board: standards, submission packs, dispensations, minutes, registers, and 32 evaluation questions | PDF, email (.eml), Excel, JSONL | 0.7 MB | Release pending |

## Why use them

- **Pinned and verifiable.** Files are published as release assets with a `SHA256SUMS` file. labagent refuses a download whose checksum does not match.
- **Realistic formats.** The ARB corpus is PDF, email and Excel, as an enterprise holds it. It teaches PDF table extraction, header and footer noise, and email threads that change an earlier decision.
- **Built to be evaluated.** Each dataset ships with questions, expected source documents and expected facts. The ARB set includes conflicting standards, an expired dispensation and questions with no answer.
- **Honest limits.** Each data card lists known gaps and what was measured.

## Quick start

SEC 10-K filings on Databricks (Lakebase with pgvector), as a step-by-step notebook tutorial (ships in the next labagent release; install from GitHub until then):

```bash
pip install 'labagent[rag] @ git+https://github.com/becloudready/labagent'
labagent launch rag-sec-tutorial --name demo
labagent destroy rag-sec-tutorial --name demo
```

ARB corpus on your laptop, with Chroma and local embeddings (after the release is published):

```bash
pip install 'labagent[rag-local]'
# download arb-2026.10.chunks.jsonl.gz from the release, then:
python3 -c "import gzip,json; from labagent.ai.rag import RAGLabClient; r=RAGLabClient(vector_db='chroma'); r.ingest_chunks([json.loads(l) for l in gzip.open('arb-2026.10.chunks.jsonl.gz','rt')]); print(r.query('Which gate applies to a new SaaS tool?').answer)"
```

## Verify a download

```bash
shasum -a 256 -c SHA256SUMS
```

## Licences

| Dataset | Terms |
|---|---|
| `sec-10k` | Text derived from filings on SEC EDGAR. Credit the SEC as the source. No warranty. Not investment advice |
| `arb` | The fictional Meridian content is provisionally CC BY 4.0 (author: BeCloudReady). Public references keep their own licence, source URL and attribution in each file: CC BY 4.0, Open Government Licence v3.0, MIT or CC0 |

## Contribute

Found a wrong fact or a broken question? Open an issue. New dataset ideas for RAG, text-to-SQL and agent labs are welcome.

Maintained by [BeCloudReady](https://becloudready.com/).
