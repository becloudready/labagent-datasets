"""Render a Markdown document (the subset used in arb/docs) as a corporate-looking PDF, deterministically.

Why PDF: ARB records are circulated as PDFs. A PDF puts the same text through a harder path than Markdown: the header and footer repeat on
every page, tables are drawn as cells rather than rows, and page breaks split sections. That is the point of this dataset, so the PDFs look like
real documents: a title block with a metadata table, a repeating header and footer ("Page n of N"), bookmarks for each section, and a diagonal
watermark on superseded documents.

Needs reportlab (BSD). Output is byte-for-byte reproducible (rl_config.invariant).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.flowables import Flowable

rl_config.invariant = 1

ORG = "Meridian Communications"
DEPT = "Enterprise Architecture"
NAVY = colors.HexColor("#1F3A5F")
GREY = colors.HexColor("#5A6472")
LIGHT = colors.HexColor("#E8EDF3")
PAGE_W, PAGE_H = letter
MARGIN = 0.9 * inch

_base = getSampleStyleSheet()
BODY = ParagraphStyle("Body", parent=_base["BodyText"], fontName="Helvetica", fontSize=10, leading=13.5, alignment=TA_LEFT, spaceAfter=6)
H1 = ParagraphStyle("Doc Title", parent=_base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=_base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=5)
H3 = ParagraphStyle("H3", parent=_base["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.black, spaceBefore=8, spaceAfter=4)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=8.5, leading=10.5, spaceAfter=0)
CELL_B = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
META_K = ParagraphStyle("MetaK", parent=CELL, fontName="Helvetica-Bold", textColor=NAVY)


def _inline(text: str) -> str:
    """Markdown inline markup to reportlab markup. Escapes first, then bold and italic."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", t)
    return t


class Bookmark(Flowable):
    """Zero-size flowable that adds a PDF bookmark (outline entry) at its position."""

    def __init__(self, title: str, key: str, level: int = 0):
        super().__init__()
        self.title, self.key, self.level = title, key, level
        self.width = self.height = 0

    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, level=self.level, closed=False)


def _table(rows: List[List[str]], width: float) -> Table:
    ncol = len(rows[0])
    weights = [max(8, min(60, max(len(r[i]) for r in rows))) for i in range(ncol)]
    total = sum(weights)
    widths = [width * w / total for w in weights]
    data = [[Paragraph(_inline(c), CELL_B if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C1CC")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F9")])]))
    return t


def md_to_flowables(body: str, width: float, doc_key: str) -> List:
    out: List = []
    lines = body.splitlines()
    i, n_sec = 0, 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("# "):
            i += 1                                                       # the title is drawn by the title block
        elif ln.startswith("## "):
            n_sec += 1
            title = ln[3:].strip()
            out += [Bookmark(title, f"{doc_key}-s{n_sec}"), Paragraph(_inline(title), H2)]
            i += 1
        elif ln.startswith("### "):
            out.append(Paragraph(_inline(ln[4:].strip()), H3))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            out += [_table(rows, width), Spacer(1, 8)]
        elif re.match(r"^\s*([-*]) ", ln) or re.match(r"^\s*\d+\. ", ln):
            numbered = bool(re.match(r"^\s*\d+\. ", ln))
            items = []
            while i < len(lines) and (re.match(r"^\s*([-*]) ", lines[i]) or re.match(r"^\s*\d+\. ", lines[i])):
                items.append(re.sub(r"^\s*(?:[-*]|\d+\.) ", "", lines[i]))
                i += 1
            out.append(ListFlowable([ListItem(Paragraph(_inline(t), BODY), leftIndent=14) for t in items],
                                    bulletType="1" if numbered else "bullet", start=1 if numbered else "•", leftIndent=14, bulletFontSize=9))
        else:
            para = [ln.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*([-*]|\d+\.) )", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(Paragraph(_inline(" ".join(para)), BODY))
    return out


class _NumberedCanvas(rl_canvas.Canvas):
    """Two-pass canvas so the footer can say 'Page n of N'."""

    def __init__(self, *a, **kw):
        self._decor = kw.pop("decor")
        super().__init__(*a, **kw)
        self._saved: List[dict] = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._decor(self, self._pageNumber, total)
            super().showPage()
        super().save()


def render_pdf(path: Path, fm: Dict[str, str], body: str) -> None:
    """fm is the document's front matter: doc_id, title, version, status, owner, effective_date, ..."""
    doc_id, title = fm["doc_id"], fm["title"]
    superseded = fm.get("status") == "superseded"

    def decor(c: rl_canvas.Canvas, page: int, total: int) -> None:
        c.saveState()
        if superseded:
            c.setFillColor(colors.Color(0.85, 0.2, 0.2, alpha=0.13))
            c.setFont("Helvetica-Bold", 78)
            c.translate(PAGE_W / 2, PAGE_H / 2)
            c.rotate(35)
            c.drawCentredString(0, 0, "SUPERSEDED")
            c.rotate(-35)
            c.translate(-PAGE_W / 2, -PAGE_H / 2)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN, PAGE_H - 0.55 * inch, f"{ORG} | {DEPT}")
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.55 * inch, doc_id if doc_id.upper().endswith("V" + str(fm.get("version", ""))) else f"{doc_id} v{fm.get('version', '')}".strip())
        c.setStrokeColor(colors.HexColor("#B8C1CC"))
        c.line(MARGIN, PAGE_H - 0.62 * inch, PAGE_W - MARGIN, PAGE_H - 0.62 * inch)
        c.line(MARGIN, 0.62 * inch, PAGE_W - MARGIN, 0.62 * inch)
        c.drawString(MARGIN, 0.45 * inch, "Internal use only. Uncontrolled when printed.")
        c.drawRightString(PAGE_W - MARGIN, 0.45 * inch, f"Page {page} of {total}")
        c.restoreState()

    width = PAGE_W - 2 * MARGIN
    meta_rows = [("Document ID", doc_id), ("Version", fm.get("version", "")), ("Status", fm.get("status", "").capitalize()), ("Owner", fm.get("owner", "")),
                 ("Effective date", fm.get("effective_date", "")), ("Classification", "Internal")]
    meta = Table([[Paragraph(k, META_K), Paragraph(_inline(v), CELL)] for k, v in meta_rows if v], colWidths=[1.3 * inch, width - 1.3 * inch])
    meta.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C1CC")),
                              ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    story = [Paragraph(_inline(title), H1), meta, Spacer(1, 10)] + md_to_flowables(body, width, doc_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=0.85 * inch, bottomMargin=0.85 * inch,
                            title=title, author=f"{ORG} {DEPT}", subject=doc_id, creator=f"{ORG} document management", invariant=1)
    doc.build(story, canvasmaker=lambda *a, **kw: _NumberedCanvas(*a, decor=decor, **kw))
