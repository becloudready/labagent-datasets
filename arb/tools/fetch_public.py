#!/usr/bin/env python3
"""Fetch the PUBLIC reference documents of the ARB dataset into arb/public/ with provenance.

Only sources whose licence allows redistribution with attribution are listed here. Each saved file starts with a front-matter block
(source URL, licence, retrieval date, attribution, what was changed) because CC BY 4.0 and OGL v3.0 both require attribution and a
statement of changes. The dataset build never touches the network: it reads the files this tool wrote.

    python3 arb/tools/fetch_public.py            # re-fetch everything
Needs: pandoc on PATH.
"""
import datetime
import html as htmllib
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public"
UA = "Mozilla/5.0 labagent-datasets (+https://github.com/becloudready/labagent-datasets)"
GOOGLE = "https://docs.cloud.google.com/architecture/framework"
CC_BY = "Creative Commons Attribution 4.0 (CC BY 4.0)"

# (slug, title, url, licence, attribution, extractor)
SOURCES = [
    ("gcp-af-overview", "Google Cloud Well-Architected Framework: overview", GOOGLE, CC_BY, "Google LLC", "article"),
    ("gcp-af-operational-excellence", "Google Cloud Well-Architected Framework: Operational excellence pillar", GOOGLE + "/operational-excellence", CC_BY, "Google LLC", "article"),
    ("gcp-af-security", "Google Cloud Well-Architected Framework: Security, privacy, and compliance pillar", GOOGLE + "/security-privacy-compliance", CC_BY, "Google LLC", "article"),
    ("gcp-af-reliability", "Google Cloud Well-Architected Framework: Reliability pillar", GOOGLE + "/reliability", CC_BY, "Google LLC", "article"),
    ("gcp-af-cost", "Google Cloud Well-Architected Framework: Cost optimization pillar", GOOGLE + "/cost-optimization", CC_BY, "Google LLC", "article"),
    ("gcp-af-performance", "Google Cloud Well-Architected Framework: Performance optimization pillar", GOOGLE + "/performance-optimization", CC_BY, "Google LLC", "article"),
    ("uk-tcop", "The Technology Code of Practice (UK Government)", "https://www.gov.uk/guidance/the-technology-code-of-practice",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-use-cloud-first", "Technology Code of Practice: Use cloud first", "https://www.gov.uk/guidance/use-cloud-first",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-make-things-secure", "Technology Code of Practice: Make things secure", "https://www.gov.uk/guidance/make-things-secure",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-make-privacy-integral", "Technology Code of Practice: Make privacy integral", "https://www.gov.uk/guidance/make-privacy-integral",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-make-use-of-open-standards", "Technology Code of Practice: Make use of open standards", "https://www.gov.uk/guidance/make-use-of-open-standards",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-integrate-and-adapt-technology", "Technology Code of Practice: Integrate and adapt technology", "https://www.gov.uk/guidance/integrate-and-adapt-technology",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-make-better-use-of-data", "Technology Code of Practice: Make better use of data", "https://www.gov.uk/guidance/make-better-use-of-data",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-define-your-purchasing-strategy", "Technology Code of Practice: Define your purchasing strategy", "https://www.gov.uk/guidance/define-your-purchasing-strategy",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("uk-tcop-make-your-technology-sustainable", "Technology Code of Practice: Make your technology sustainable", "https://www.gov.uk/guidance/make-your-technology-sustainable",
     "Open Government Licence v3.0", "Contains public sector information licensed under the Open Government Licence v3.0. Crown copyright.", "main"),
    ("c4-abstractions", "C4 model: Abstractions", "https://c4model.com/abstractions", CC_BY, "Simon Brown, c4model.com", "main"),
    ("c4-software-system", "C4 model: Software system", "https://c4model.com/abstractions/software-system", CC_BY, "Simon Brown, c4model.com", "main"),
    ("c4-container", "C4 model: Container", "https://c4model.com/abstractions/container", CC_BY, "Simon Brown, c4model.com", "main"),
    ("c4-component", "C4 model: Component", "https://c4model.com/abstractions/component", CC_BY, "Simon Brown, c4model.com", "main"),
    ("madr-template", "MADR: Markdown Architectural Decision Records, template", "https://raw.githubusercontent.com/adr/madr/main/template/adr-template.md",
     "MIT OR CC0-1.0", "MADR contributors (https://adr.github.io/madr/)", "raw"),
]


def fetch(url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return r.read().decode("utf8", errors="replace")


def extract(raw: str, how: str) -> str:
    if how == "raw":
        return raw
    pats = {"article": r"<article[^>]*>(.*?)</article>", "main": r"<main[^>]*>(.*?)</main>",
            "govspeak": r'<div class="govuk-govspeak[^"]*"[^>]*>(.*)'}
    m = re.search(pats[how], raw, re.S)
    if not m:
        raise RuntimeError(f"no {how} element found")
    body = m.group(1)
    for junk in (r"<script.*?</script>", r"<style.*?</style>", r"<nav.*?</nav>", r"<devsite-[^>]*>.*?</devsite-[^>]*>", r"<button.*?</button>",
                 r"<svg.*?</svg>", r"<figure.*?</figure>"):
        body = re.sub(junk, "", body, flags=re.S)
    return body


def to_markdown(fragment: str) -> str:
    p = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"], input=fragment, capture_output=True, text=True, check=True)
    text = p.stdout
    text = re.sub(r"<[^>]+>", "", text)                       # leftover tags
    # page chrome that survives conversion: breadcrumb bullets, collection prompts, "view on one page" notices
    text = re.sub(r"(?m)^- *\n\n\s*\n\n\s+(Documentation|Cloud Architecture Center)\s*$\n?", "", text)
    text = re.sub(r"Stay organized with collections\s+Save and categorize content based on your preferences\.\s*", "", text)
    text = re.sub(r"(?m)^To view the content in the .*? see View on one page\.\s*$", "", text)
    text = re.sub(r"(?m)^Last reviewed .*$", "", text)
    text = re.sub(r"(?m)^- Home\s*$\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", htmllib.unescape(text)).strip()
    return text


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    failed = 0
    for slug, title, url, licence, attribution, how in SOURCES:
        try:
            raw = fetch(url)
            body = raw if how == "raw" else to_markdown(extract(raw, how))
        except Exception as e:                                    # keep going, report at the end
            print(f"FAIL {slug}: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1
            continue
        head = (f"---\ndoc_id: PUB-{slug}\ntitle: {title}\nsource_url: {url}\nlicense: {licence}\nattribution: {attribution}\nretrieved: {today}\n"
                "changes: Converted from HTML to Markdown; navigation and images removed. Wording unchanged.\n---\n\n")
        (OUT / f"{slug}.md").write_text(head + (f"# {title}\n\n" if how != "raw" and not body.lstrip().startswith("#") else "") + body + "\n")
        print(f"ok   {slug}: {len(body):,} chars")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
