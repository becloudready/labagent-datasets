"""Minutes and replies as .eml files (RFC 5322), the way they are really circulated. Deterministic: every header is derived from the data."""
from __future__ import annotations

import datetime as dt
import textwrap
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import format_datetime
from typing import Dict, List, Optional

import submissions as S

SIGNATURE = ["--", "{name}", "{role} | Enterprise Architecture", "Meridian Communications",
             "This message is for ARB members. Please do not forward it outside Meridian."]


def _tz(d: dt.date) -> dt.timezone:
    """US Eastern: daylight time from the second Sunday of March to the first Sunday of November (2026: 8 March to 1 November)."""
    return dt.timezone(dt.timedelta(hours=-4 if dt.date(2026, 3, 8) <= d < dt.date(2026, 11, 1) else -5))


def _name(key: str) -> str:
    return S.PEOPLE[key].split(" (")[0]


def _role(key: str) -> str:
    return S.PEOPLE[key].split(" (")[1].rstrip(")").split(", ")[-1] if " (" in S.PEOPLE[key] else ""


def _addr(key: str) -> str:
    return f"{_name(key)} <{S.EMAILS[key]}>"


def _stamp(date_str: str) -> dt.datetime:
    d = dt.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    return d.replace(tzinfo=_tz(d.date()))


def _sig(key: str) -> List[str]:
    return [l.format(name=_name(key), role=_role(key)) for l in SIGNATURE]


def minutes_message(date: dt.date, sent: dt.datetime, present: List[str], absent: Optional[str], items: List[Dict], others: List[Dict]) -> EmailMessage:
    lines = ["Hi all,", "",
             f"Minutes from the ARB working session on {date.strftime('%A %d %B %Y')} are below. Please reply with any corrections by end of day Friday.", "",
             "ATTENDANCE", f"Present: {'; '.join(present)}.", f"Absent: {S.PEOPLE[absent] if absent else 'none'}. Quorum (Chair or Deputy plus three domain architects): met.", "", "DECISIONS"]
    for n, it in enumerate(items, 1):
        lines += ["", f"{n}) {it['id']} {it['name']} ({it['gate']}, {it['tier_name']})", f"   Decision: {it['outcome']}"]
        lines += textwrap.wrap(f"Discussion: {it['discussion']}", 96, initial_indent="   ", subsequent_indent="   ")
        if it["conditions"]:
            lines.append("   Conditions:")
            lines += [f"     {c['id']}  {c['text']} Owner: {c['owner']}. Due: {c['due']}." for c in it["conditions"]]
        if it["dispensations"]:
            lines.append(f"   Dispensation granted: {', '.join(it['dispensations'])}.")
    if others:
        lines += ["", "OTHER DECISIONS AT THIS SESSION"] + [f"- {o['id']} {o['name']} ({o['gate']}, {o['tier_name']}): {o['outcome']}." for o in others]
    lines += ["", "NEXT SESSION", "Tuesday at 10:00. Minutes are published within 2 business days.", "", "Thanks,", "Dev", ""] + _sig("front")
    m = EmailMessage(policy=SMTP)
    m["From"] = _addr("front")
    m["To"] = f"ARB Members <{S.ARB_LIST}>"
    m["Cc"] = "Enterprise Architecture Office <ea-office@meridian.example>"
    m["Subject"] = f"ARB working session minutes, {date.isoformat()}"
    m["Date"] = format_datetime(sent)
    m["Message-ID"] = f"<arb-minutes-{date.isoformat()}@meridian.example>"
    m.set_content("\n".join(lines) + "\n", cte="7bit")
    return m


def reply_message(original: EmailMessage, followup: Dict) -> EmailMessage:
    """A reply that quotes the start of the original, as mail clients do."""
    quoted = [f"> {l}" for l in original.get_content().splitlines()[:14]]
    sent = _stamp(followup["sent"])
    sender = followup["sender"]
    body = followup["body"]
    lines = []
    for b in body:
        lines.append(b)
        if b.startswith("Hi") or b.endswith(","):
            lines.append("")
    text = "\n".join(lines).rstrip() + "\n\n" + "\n".join(_sig(sender)) + f"\n\nOn {original['Date']}, {original['From']} wrote:\n" + "\n".join(quoted) + "\n> ...\n"
    m = EmailMessage(policy=SMTP)
    m["From"] = _addr(sender)
    m["To"] = original["From"]
    m["Cc"] = f"ARB Members <{S.ARB_LIST}>"
    m["Subject"] = "Re: " + original["Subject"]
    m["Date"] = format_datetime(sent)
    m["Message-ID"] = f"<{original['Message-ID'][1:-1].split('@')[0]}-{followup['suffix']}@meridian.example>"
    m["In-Reply-To"] = original["Message-ID"]
    m["References"] = original["Message-ID"]
    m.set_content(text, cte="7bit")
    return m


def to_bytes(m: EmailMessage) -> bytes:
    return m.as_bytes()
