# ARB dataset: an Architecture Review Board corpus for RAG labs

A fictional telecom, **Meridian Communications**, and the records its Architecture Review Board (ARB) would hold: process, standards, submissions, decisions, dispensations, minutes, and a throughput workbook. Plus public architecture guidance that is licensed for reuse. Built so the same corpus can be loaded into different RAG implementations and compared.

Everything about Meridian is invented. No real company, customer, or employee appears.

| | |
|---|---|
| Documents | 80: 56 Meridian documents, 4 register tables, 20 public references |
| Chunks | 235, about 1,100 characters each, with metadata |
| Evaluation questions | 30 (see below), each with expected source documents and expected facts |
| As of | 2026-10-15 (the date inside the dataset: it decides which dispensations have expired) |
| Size | chunks 70 KB, corpus archive 0.3 MB |

## What is in the corpus

| Folder | Content | Count |
|---|---|---|
| `docs/process` | ARB charter, Front Door guide (request type to gate, form, tier), gate definitions, forms catalog, service levels, dispensation policy, appeals, tracker schema, throughput definitions | 9 |
| `docs/standards` | Nine current standards with numbered requirements (cloud, identity, data, API, resilience, logging, AI, third-party risk, integration) and one superseded version | 10 |
| `docs/submissions` | Fifteen full submission packs with a standards compliance matrix, options, decision, and conditions | 15 |
| `docs/dispensations` | Seven dispensation requests with conditions, owners, and expiry. Status is as of 2026-10-15 | 7 |
| `docs/minutes` | Minutes of every working session that decided a full submission | 15 |
| `docs/registers` | Governance log, dispensation register, ARB Submission Tracker, throughput workbook (CSV, and Excel in the archive) | 4 |
| `public` | Public guidance with source, licence, and attribution recorded in each file | 20 |

The log and workbook hold 76 gate events (74 decided, 2 still in review): 19 from the 15 full submissions plus 57 from smaller submissions that have a row but no pack.

## Public sources and licences

Included, because the licence allows redistribution with attribution (verified on the source page or repository on 2026-10-23):

| Source | Licence | Files |
|---|---|---|
| [Google Cloud Well-Architected Framework](https://docs.cloud.google.com/architecture/framework) (overview and five pillars) | CC BY 4.0 | 6 |
| [UK Technology Code of Practice](https://www.gov.uk/guidance/the-technology-code-of-practice) (index and eight principles) | Open Government Licence v3.0 | 9 |
| [C4 model](https://c4model.com/abstractions) (abstractions, software system, container, component) | CC BY 4.0 | 4 |
| [MADR decision record template](https://github.com/adr/madr) | MIT or CC0 | 1 |

Each file keeps its source URL, licence, retrieval date, and a note of what was changed (HTML converted to Markdown, navigation removed, wording unchanged). Re-fetch with `python3 arb/tools/fetch_public.py`.

**Link only, not included:**

| Source | Why |
|---|---|
| Azure Well-Architected Framework, AWS Well-Architected Framework | Licence could not be confirmed from a public repository |
| NIST Cybersecurity Framework 2.0 | Expected to be freely reusable, but the reuse statement was not confirmed here. Verify before including |
| TOGAF (The Open Group) | Proprietary |
| GitLab handbook ARB page | CC BY-SA 4.0. Share-alike would extend to a dataset that includes it |
| Real ARB processes (state agencies, universities) | No clear reuse licence found. Useful as structural references only |

The Meridian content is provisionally licensed CC BY 4.0 (author: BeCloudReady). Confirm that before publishing.

## Evaluation set

`arb-<version>.eval.jsonl`, 30 questions. Fields: `id`, `category`, `question`, `expected_docs` (any one of these documents in the retrieved set counts as a hit), `expected_facts` (strings a correct answer should contain), `expect_decline` (the corpus does not answer it, so a good system says so), and for some questions a `trap` note for instructors.

Categories: `navigator` (which gate, form, and service level), `conflict` (two standards disagree), `version` (a superseded standard exists), `temporal` (dates decide the answer), `multi-hop` (needs two documents), `aggregate` (a number from the workbook), `public`, `process`, `decline`.

Answers that depend on numbers or dates are computed from the data at build time, so they cannot drift from the documents.

## Try it locally

```bash
pip install 'labagent[rag-local]'
python3 arb/tools/build.py --version 2026.10           # writes arb/dist
python3 arb/tools/try_local.py --top-k 5               # retrieval check, no LLM needed
python3 arb/tools/try_local.py --top-k 5 --answers     # also asks your LLM (Groq key, or local Ollama)
```

Or in Python:

```python
import gzip, json
from labagent.ai.rag import RAGLabClient
rows = [json.loads(l) for l in gzip.open("arb/dist/arb-2026.10.chunks.jsonl.gz", "rt")]
rag = RAGLabClient(vector_db="chroma"); rag.ingest_chunks(rows)
print(rag.query("Which gate and form apply to a new SaaS survey tool?", where={"doc_type": "process"}).answer)
```

Metadata on every chunk: `doc_id`, `doc_type`, `title`, `section`, `status` (current or superseded for standards; Active, Expired, or Revoked for dispensations), `version`, `owner`, `effective_date`, `source_system`, `source_path`, `license`, and for public references `url` and `attribution`.

## Measured so far (local, 2026-10-23)

Chroma with `all-MiniLM-L6-v2`, top 5, labagent hybrid rerank: **23 of 27 answerable questions retrieve an expected document (85%)**. The misses are the kind a lab should show: questions that need a scan of a register, date arithmetic across documents, or a broad "which ones" question. Indexing takes about 2 seconds.

Answer quality was checked on 6 of the questions with two local models (Ollama, same retrieval). The three questions with no answer in the corpus are the hard part:

| Model | Declined the 3 unanswerable questions | Facts present in the 3 answerable answers checked |
|---|---|---|
| qwen2.5-coder 0.5B | 0 of 3. It invented a vendor name and used the Tier 1 cost limit as an approval limit | 1 of 4 questions fully right |
| qwen2.5-coder 7B | 2 of 3. It still mistook the Tier 3 cost trigger for an approval limit | 2 of 4 questions fully right |

Fact and refusal checks are simple string matches, so treat these numbers as a rough guide. A hosted model was not tested.

## What is not built yet

The outline's other implementations need more than documents: Microsoft 365 Copilot needs the content in SharePoint plus mail and Teams history, and Atlassian Rovo needs Confluence pages and Jira issues. This release is the document corpus (Markdown, CSV, Excel) in a folder layout that can be uploaded to SharePoint. Emails, Teams chats, and Confluence or Jira renderings are future work and would be generated from the same source data.

The instructor notes are in [INSTRUCTOR.md](INSTRUCTOR.md) and are not part of the corpus archive.
