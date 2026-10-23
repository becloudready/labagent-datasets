# sec-10k: SEC 10-K filings for RAG labs (release 2026.10)

Section-split text from recent SEC 10-K annual reports, chunked for retrieval (RAG) workshops.

| | |
|---|---|
| Passages | 1,880 |
| Filings | 10 (AAPL, CVX, JPM, PFE, WMT; two fiscal years each) |
| Sections | Item 1 Business, Item 1A Risk Factors, Item 7 MD&A |
| As of | 2026-10-22 |
| Size | about 0.5 MB compressed |

**Files** (in the release): `sec-10k-2026.10.chunks.jsonl.gz`, `sec-10k-2026.10.manifest.json`, `SHA256SUMS`.

**Record format** (one JSON object per line):
`id`, `title`, `content`, `meta` with `ticker`, `company`, `form`, `fiscal_year` (year of the period end date), `item`, `section`, `filed`, `url` (the filing on sec.gov).

**Use with labagent** (the `rag-sec-filings` pack is in labagent 0.2.1 on PyPI)
```bash
pip install 'labagent[rag]'
labagent launch rag-sec-filings --name sec --param profile=<databricks-profile>
```

**Verify a download**
```bash
shasum -a 256 -c SHA256SUMS
```

## Known limitations

- **JPM and CVX have no Item 7 (MD&A).** Those filings place or incorporate the discussion elsewhere, and the parser only reads Item 7.
- **Tables are flattened to text.** Do not rely on numbers that come from tables.
- A few chunks are bare headings or page numbers, and a few exceed the 1,200 character target.
- Walmart's fiscal year ends in January, so its `fiscal_year` 2026 is the year ended January 2026.
- No embeddings are included: embed with the model of your choice.

## Source and terms

Text is derived from filings published on the SEC's [EDGAR](https://www.sec.gov/edgar) system. Each record links to its original filing.
Please credit the SEC as the source. Provided as is, with no warranty. Informational only, not investment advice.
