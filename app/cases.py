"""Paid tier prototype: a victim hands over their case, Fraud Aid processes the claim.

Local SQLite plus files under the data dir. This is a pilot-grade store for development:
before real victims use it, it needs EU hosting, encryption at rest, a retention policy,
a data processing review and lawyer-approved terms (see README).
"""

import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from . import tools
from .i18n import TERMS, pick
from .plan import Answers, build_plan

TERMS_VERSION = "draft-2026-11"
STATUSES = ["received", "in_review", "claim_sent", "escalated", "won", "lost", "withdrawn"]
STATUS_LABEL = {
    "received": "Received",
    "in_review": "We are reviewing your case",
    "claim_sent": "Claim sent to your bank",
    "escalated": "Escalated to Ombudsfin or a lawyer",
    "won": "Money recovered",
    "lost": "Closed without recovery",
    "withdrawn": "Withdrawn",
}
MAX_FILES = 10
MAX_BYTES = 10 * 1024 * 1024
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".heic", ".txt"}

def terms(lang: str = "en") -> dict:
    return {"version": TERMS_VERSION, **pick(TERMS, lang)}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def iban_ok(value: str) -> bool:
    v = re.sub(r"\s+", "", value).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", v):
        return False
    digits = "".join(str(int(c, 36)) for c in v[4:] + v[:4])
    return int(digits) % 97 == 1


class Contact(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)
    address: str = Field(min_length=5, max_length=200)
    iban: str = Field(max_length=40)

    @field_validator("iban")
    @classmethod
    def _iban(cls, v: str) -> str:
        if not iban_ok(v):
            raise ValueError("That IBAN does not look valid.")
        return re.sub(r"\s+", "", v).upper()


class Consent(BaseModel):
    privacy: bool
    terms: bool
    mandate: bool
    signature_name: str = Field(min_length=2, max_length=100)
    share_intel: bool = False

    @field_validator("privacy", "terms", "mandate")
    @classmethod
    def _required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("This consent is required.")
        return v


class CaseCreate(BaseModel):
    answers: Answers
    summary: str = Field(default="", max_length=3000)
    contact: Contact
    consent: Consent


def db() -> sqlite3.Connection:
    tools.DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(tools.DATA / "cases.db")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL,
            level TEXT NOT NULL, answers TEXT NOT NULL, summary TEXT NOT NULL,
            full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, address TEXT NOT NULL, iban TEXT NOT NULL,
            terms_version TEXT NOT NULL, mandate_signature TEXT NOT NULL, share_intel INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY, case_id TEXT NOT NULL, original_name TEXT NOT NULL, stored_name TEXT NOT NULL,
            content_type TEXT NOT NULL, size INTEGER NOT NULL, uploaded_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, at TEXT NOT NULL, kind TEXT NOT NULL,
            note TEXT NOT NULL, public INTEGER NOT NULL DEFAULT 1
        );
        """
    )
    return con


def _event(con: sqlite3.Connection, case_id: str, kind: str, note: str, public: bool = True) -> None:
    con.execute("INSERT INTO events (case_id, at, kind, note, public) VALUES (?,?,?,?,?)", (case_id, _now(), kind, note, int(public)))


class NotEligible(Exception):
    pass


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class BadUpload(Exception):
    pass


def create_case(p: CaseCreate) -> tuple[str, str]:
    plan = build_plan(p.answers, p.summary or p.answers.free_text)
    if not plan.can_offer_help:
        raise NotEligible("From your answers we cannot take this case on, but your plan still applies.")
    case_id = "FA-" + "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
    token = secrets.token_urlsafe(24)
    with db() as con:
        con.execute(
            "INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                case_id, _hash(token), _now(), "received", plan.verdict.level, p.answers.model_dump_json(), plan.summary,
                p.contact.full_name, p.contact.email, p.contact.phone, p.contact.address, p.contact.iban,
                TERMS_VERSION, p.consent.signature_name, int(p.consent.share_intel),
            ),
        )
        _event(con, case_id, "created", "We received your case.")
    return case_id, token


def _check(con: sqlite3.Connection, case_id: str, token: str) -> sqlite3.Row:
    row = con.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not row:
        raise NotFound()
    if not hmac.compare_digest(row["token_hash"], _hash(token or "")):
        raise Forbidden()
    return row


def victim_view(case_id: str, token: str) -> dict:
    with db() as con:
        row = _check(con, case_id, token)
        files = con.execute("SELECT id, original_name, size, uploaded_at FROM evidence WHERE case_id = ? ORDER BY uploaded_at", (case_id,)).fetchall()
        events = con.execute("SELECT at, kind, note FROM events WHERE case_id = ? AND public = 1 ORDER BY id", (case_id,)).fetchall()
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "status": row["status"],
            "status_label": STATUS_LABEL[row["status"]],
            "files": [dict(f) for f in files],
            "events": [dict(e) for e in events],
        }


def add_evidence(case_id: str, token: str, filename: str, content_type: str, data: bytes) -> dict:
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise BadUpload("Allowed files: PDF, PNG, JPG, HEIC or TXT.")
    if not data or len(data) > MAX_BYTES:
        raise BadUpload("Each file must be between 1 byte and 10 MB.")
    with db() as con:
        _check(con, case_id, token)
        n = con.execute("SELECT COUNT(*) FROM evidence WHERE case_id = ?", (case_id,)).fetchone()[0]
        if n >= MAX_FILES:
            raise BadUpload("You can upload up to 10 files.")
        stored = uuid.uuid4().hex + ext
        folder = tools.DATA / "evidence" / case_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / stored).write_bytes(data)
        eid = uuid.uuid4().hex
        clean = re.sub(r"[^\w.\- ]", "_", Path(filename).name)[:100]
        con.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?)", (eid, case_id, clean, stored, content_type or "", len(data), _now()))
        _event(con, case_id, "evidence", f"File added: {clean}")
        return {"id": eid, "original_name": clean, "size": len(data)}


def delete_case(case_id: str, token: str) -> None:
    with db() as con:
        _check(con, case_id, token)
        con.execute("DELETE FROM evidence WHERE case_id = ?", (case_id,))
        con.execute("DELETE FROM events WHERE case_id = ?", (case_id,))
        con.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    folder = tools.DATA / "evidence" / case_id
    if folder.exists():
        for f in folder.iterdir():
            f.unlink()
        folder.rmdir()


# ---- Back office ---------------------------------------------------------------------------


def admin_list() -> list[dict]:
    with db() as con:
        rows = con.execute(
            "SELECT c.id, c.created_at, c.status, c.level, c.full_name, json_extract(c.answers, '$.bank') AS bank, "
            "json_extract(c.answers, '$.amount_eur') AS amount, (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.id) AS files "
            "FROM cases c ORDER BY c.created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def admin_get(case_id: str) -> dict:
    with db() as con:
        row = con.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        if not row:
            raise NotFound()
        files = con.execute("SELECT id, original_name, size, uploaded_at FROM evidence WHERE case_id = ?", (case_id,)).fetchall()
        events = con.execute("SELECT at, kind, note, public FROM events WHERE case_id = ? ORDER BY id", (case_id,)).fetchall()
    answers = Answers.model_validate_json(row["answers"])
    plan = build_plan(answers, row["summary"])
    docs = [s.doc.model_dump() for s in plan.steps if s.doc]
    data = {k: row[k] for k in row.keys() if k not in ("token_hash", "answers")}
    return {**data, "share_intel": bool(row["share_intel"]), "answers": json.loads(row["answers"]), "docs": docs, "files": [dict(f) for f in files], "events": [dict(e) for e in events], "statuses": STATUSES}


def admin_set_status(case_id: str, status: str, note: str) -> None:
    if status not in STATUSES:
        raise BadUpload("Unknown status.")
    with db() as con:
        if not con.execute("SELECT 1 FROM cases WHERE id = ?", (case_id,)).fetchone():
            raise NotFound()
        con.execute("UPDATE cases SET status = ? WHERE id = ?", (status, case_id))
        _event(con, case_id, "status", note.strip()[:300] or f"status:{status}")


def admin_file(case_id: str, evidence_id: str) -> tuple[Path, str, str]:
    with db() as con:
        row = con.execute("SELECT * FROM evidence WHERE id = ? AND case_id = ?", (evidence_id, case_id)).fetchone()
    if not row:
        raise NotFound()
    return tools.DATA / "evidence" / case_id / row["stored_name"], row["original_name"], row["content_type"]
