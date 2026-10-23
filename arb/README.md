# ARB dataset: an Architecture Review Board corpus for RAG labs

A fictional telecom, **Meridian Communications**, and the records its Architecture Review Board (ARB) would hold, in the formats it would hold them: **PDF** for standards, policies, forms, submission packs and dispensations; **email (.eml)** for minutes and the replies that change them; **Excel and CSV** for the registers. Plus public architecture guidance that is licensed for reuse. Built so the same corpus can be loaded into different RAG implementations and compared.

Everything about Meridian is invented. No real company, customer, or employee appears. Email addresses use the reserved `.example` domain.

| | |
|---|---|
| Corpus files | 41 PDF, 17 email, 4 Excel, 4 CSV, 20 public web pages (Markdown) |
| Documents | 82 (62 Meridian documents and emails, 20 public references) |
| Chunks | 259, about 1,000 characters each, with page numbers and metadata |
| Evaluation questions | 32, each with expected source documents and expected facts |
| As of | 2026-10-15 (the date inside the dataset: it decides which dispensations have expired) |
| Size | corpus archive 0.6 MB, chunks 75 KB |

## What is in the corpus (`corpus/` in the archive)

| Folder | Format | Content | Files |
|---|---|---|---|
| `process` | PDF | ARB charter, Front Door guide (request type to gate, form, tier), gate definitions, forms catalog, service levels, dispensation policy, appeals, tracker schema, throughput definitions | 9 |
| `standards` | PDF | Nine current standards with numbered requirements, plus one superseded version carrying a SUPERSEDED watermark | 10 |
| `submissions` | PDF | Fifteen completed ARB-F3 packs: compliance matrix, options, decision, conditions | 15 |
| `dispensations` | PDF | Seven completed ARB-F5 dispensation requests. Status is as of 2026-10-15 | 7 |
| `minutes` | email | Fifteen minutes emails sent the business day after each session, and two follow-up replies | 17 |
| `registers` | Excel + CSV | Governance log, dispensation register, ARB Submission Tracker, throughput workbook | 4 + 4 |
| `public` | Markdown | Public guidance (below), each file with source, licence, and attribution | 20 |

The PDFs look like controlled documents: a title block with a metadata table, a running header and footer ("Page n of N", "Uncontrolled when printed"), bookmarks, and tables drawn as cells. The text is selectable. They are **not scans**: there is no OCR step.

The log and workbook hold 76 gate events (74 decided, 2 still in review): 19 from the 15 full submissions plus 57 from smaller submissions that have a row but no pack.

## Why the formats matter

A PDF puts the same words through a harder path than Markdown. With the default extraction of a PDF library, the running header and footer land in the middle of your chunks, and every table row is split into one cell per line, so "STD-API-004 R6 | Conflict | Requires mutual TLS bound tokens" becomes three unrelated lines. The chunks in this release come from **extracting the actual files**:

- **PDF**: pypdf in layout mode, header and footer removed, column gaps kept as ` | `, section names taken from the PDF's own bookmarks, page numbers recorded.
- **Email**: From, To, Date and Subject kept with the body, so "who said it and when" is searchable.

`arb-<version>.chunks-naive-pdf.jsonl.gz` holds chunks from naive PDF extraction, so you can measure the difference on your own pipeline.

## Public sources and licences

Included, because the licence allows redistribution with attribution (checked on the source page or repository on 2026-10-23):

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

`arb-<version>.eval.jsonl`, 32 questions. Fields: `id`, `category`, `question`, `expected_docs` (any one of these documents in the retrieved set counts as a hit), `expected_facts` (strings a correct answer should contain), `expect_decline` (the corpus does not answer it, so a good system says so), and for some questions a `trap` note for instructors.

Categories: `navigator` (which gate, form, and service level), `conflict` (two standards disagree), `version` (a superseded standard exists), `temporal` (dates decide the answer), `multi-hop` (needs two documents), `email` (the answer exists only in a reply), `aggregate` (a number from the workbook), `public`, `process`, `decline`.

Answers that depend on numbers or dates are computed from the data at build time, so they cannot drift from the documents.

## Try it locally

```bash
pip install "labagent[rag-local]" -r arb/requirements.txt   # the requirements file is only needed to rebuild
python3 arb/tools/build.py --version 2026.10                # renders the corpus and writes arb/dist
python3 arb/tools/try_local.py --top-k 5                    # retrieval check, no LLM needed
python3 arb/tools/try_local.py --top-k 5 --naive            # same, with naive PDF extraction
python3 arb/tools/try_local.py --top-k 5 --answers          # also asks your LLM (Groq key, or local Ollama)
```

Or in Python, from the released chunks:

```python
import gzip, json
from labagent.ai.rag import RAGLabClient
rows = [json.loads(l) for l in gzip.open("arb/dist/arb-2026.10.chunks.jsonl.gz", "rt")]
rag = RAGLabClient(vector_db="chroma"); rag.ingest_chunks(rows)
print(rag.query("Which gate and form apply to a new SaaS survey tool?", where={"doc_type": "process"}).answer)
```

To ingest the **raw files** yourself (the realistic exercise), point a parser at `arb/dist/corpus/`. `labagent` reads the PDFs with pypdf's default mode, which shows the naive-extraction problems above. It does not read `.eml` files yet.

Metadata on every chunk: `doc_id`, `doc_type`, `title`, `section`, `status` (current or superseded for standards; Active, Expired, or Revoked for dispensations), `version`, `owner`, `effective_date`, `source_system`, `source_path`, `source_format`, `license`, `page_start` and `page_end` for PDFs, `sender` and `subject` for email, and for public references `url` and `attribution`.

## Measured so far (local, 2026-10-23)

Chroma with `all-MiniLM-L6-v2`, top 5, labagent's hybrid rerank, 29 answerable questions:

| PDF extraction | Retrieves an expected document |
|---|---|
| Layout-aware (this release's chunks) | 25 of 29 (86%) |
| Naive (default pypdf) | 24 of 29 (83%) |

The one-question gap understates the problem: retrieving the right document says nothing about whether a broken table row yields a correct answer, and that was not measured. The misses in both runs are the kind a lab should show: a register scan (which dispensations expire before 2027), date arithmetic across documents, and a broad "which ones" question.

Answers were checked on a handful of questions with two local models only (Ollama, same retrieval). The three questions with no answer in the corpus are the hard part: the 0.5B model answered all three anyway, and the 7B model declined two and mistook the Tier 3 cost trigger for an approval limit. On the email-only questions the 7B model found the changed due date but missed that the dispensation ends 15 days before it. Fact and refusal checks are simple string matches, so treat these as a rough guide. A hosted model was not tested.

## What is not built yet

- **Microsoft 365 Copilot** needs the content in SharePoint plus real mail and Teams history, and **Atlassian Rovo** needs Confluence pages and Jira issues. The corpus folder layout can be uploaded to SharePoint as is. Teams chats and Confluence or Jira renderings are future work and would be generated from the same source data.
- **Scanned documents.** Real archives contain scans that need OCR. These PDFs are text-based.
- **Word and PowerPoint.** Only PDF, email and Excel are produced. A Word version of the process documents would be a small addition.

The instructor notes are in [INSTRUCTOR.md](INSTRUCTOR.md) and are not part of the corpus archive.
