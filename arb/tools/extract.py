"""Reference text extraction for the corpus formats. This is what turns the real files back into text for chunking.

PDF  : pypdf in layout mode (keeps table rows on one line), then removes the repeating header and footer, collapses column gaps to " | ",
       and records the page of every line. Naive extraction (pypdf default mode) is NOT used here on purpose: it splits table rows into one
       cell per line and leaves the header and footer on every page. See try_local.py --naive to measure the difference.
EML  : headers that matter for retrieval (From, To, Date, Subject) plus the plain text body, quoted reply lines kept but marked.
"""
from __future__ import annotations

import email
import re
from email import policy
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pypdf

PageText = List[Tuple[int, str]]            # (page number starting at 1, cleaned text)


def _norm_line(line: str) -> str:
    line = re.sub(r"^\s*[\x7f\u2022\u25cf\u25aa]\s+", "- ", line)          # list bullet glyphs come through as control characters
    line = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", line).rstrip()
    lead = len(line) - len(line.lstrip())
    body = re.sub(r"\s{3,}", " | ", line.strip())          # a wide gap in layout mode is a column boundary
    return ("  " if lead >= 3 else "") + body


def pdf_pages(path: Path, naive: bool = False) -> PageText:
    reader = pypdf.PdfReader(str(path))
    out = []
    for n, p in enumerate(reader.pages, 1):
        raw = p.extract_text() if naive else p.extract_text(extraction_mode="layout")
        lines = [l.strip() for l in raw.splitlines()] if naive else [_norm_line(l) for l in raw.splitlines()]
        filled = [i for i, l in enumerate(lines) if l.strip()]
        if not naive and len(filled) >= 2:
            # page furniture: the first non-blank line is the running header, the last is the footer ("Page n of N")
            drop = set()
            if "|" in lines[filled[0]] and ("Meridian" in lines[filled[0]]):
                drop.add(filled[0])
            if "Internal use only" in lines[filled[-1]]:
                drop.add(filled[-1])
            lines = [l for i, l in enumerate(lines) if i not in drop]
        text = "\n".join(lines).strip()
        text = re.sub(r"\n\s*\n(\s*\n)+", "\n\n", text)        # collapse runs of blank lines to one: a blank line separates paragraphs
        if text:
            out.append((n, text))
    return out


def pdf_outline(path: Path) -> List[Tuple[int, str]]:
    """(page, title) for each bookmark, in document order. Real PDFs often have these; chunks use them as section names."""
    r = pypdf.PdfReader(str(path))
    entries = []

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
            else:
                entries.append((r.get_destination_page_number(it) + 1, str(it.title)))

    walk(r.outline)
    return entries


def pdf_title_block(path: Path) -> Dict[str, str]:
    info = pypdf.PdfReader(str(path)).metadata or {}
    return {"title": str(info.get("/Title", "")), "subject": str(info.get("/Subject", ""))}


def eml_text(path: Path) -> Tuple[Dict[str, str], str]:
    msg = email.message_from_bytes(path.read_bytes(), policy=policy.default)
    headers = {k: str(msg[k]) for k in ("From", "To", "Cc", "Date", "Subject", "In-Reply-To") if msg[k]}
    body = msg.get_body(preferencelist=("plain",)).get_content().replace("\r\n", "\n").replace("\r", "\n")
    return headers, body.strip()
