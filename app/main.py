import hmac
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from . import cases
from .plan import Answers, Plan, build_plan, summarize
from .tools import TIPS, save_waitlist

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Fraud Aid")


class WaitlistRequest(BaseModel):
    email: EmailStr
    consent: bool
    country: Optional[str] = None
    note: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str
    note: str = Field(default="", max_length=300)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/tips")
def tips() -> dict:
    return TIPS


@app.post("/api/plan", response_model=Plan)
async def plan(a: Answers) -> Plan:
    # The free flow never stores anything: answers are used to build the response and dropped.
    return build_plan(a, await summarize(a))


@app.post("/api/waitlist")
def waitlist(req: WaitlistRequest) -> dict:
    if not req.consent:
        raise HTTPException(400, "Consent is required.")
    save_waitlist(req.email, (req.country or "")[:40] or None, (req.note or "")[:200] or None)
    return {"ok": True}


# ---- Paid tier: the victim hands over the case -------------------------------------------------


def _guard(fn, *args):
    try:
        return fn(*args)
    except cases.NotFound:
        raise HTTPException(404, "Case not found.")
    except cases.Forbidden:
        raise HTTPException(403, "Wrong or missing case token.")
    except cases.BadUpload as e:
        raise HTTPException(400, str(e))
    except cases.NotEligible as e:
        raise HTTPException(422, str(e))


@app.get("/api/terms")
def terms() -> dict:
    return cases.TERMS


@app.post("/api/cases")
def create_case(p: cases.CaseCreate) -> dict:
    case_id, token = _guard(cases.create_case, p)
    return {"case_id": case_id, "token": token}


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, x_case_token: str = Header(default="")) -> dict:
    return _guard(cases.victim_view, case_id, x_case_token)


@app.post("/api/cases/{case_id}/evidence")
async def upload_evidence(case_id: str, file: UploadFile = File(...), x_case_token: str = Header(default="")) -> dict:
    data = await file.read(cases.MAX_BYTES + 1)
    return _guard(cases.add_evidence, case_id, x_case_token, file.filename or "", file.content_type or "", data)


@app.delete("/api/cases/{case_id}")
def delete_case(case_id: str, x_case_token: str = Header(default="")) -> dict:
    _guard(cases.delete_case, case_id, x_case_token)
    return {"deleted": True}


# ---- Back office (disabled unless FRAUD_AID_ADMIN_TOKEN is set) ---------------------------------


def _admin(token: str) -> None:
    expected = os.getenv("FRAUD_AID_ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(403, "Back office is disabled. Set FRAUD_AID_ADMIN_TOKEN.")
    if not hmac.compare_digest(expected, token or ""):
        raise HTTPException(403, "Wrong admin token.")


@app.get("/api/admin/cases")
def admin_cases(x_admin_token: str = Header(default="")) -> list:
    _admin(x_admin_token)
    return cases.admin_list()


@app.get("/api/admin/cases/{case_id}")
def admin_case(case_id: str, x_admin_token: str = Header(default="")) -> dict:
    _admin(x_admin_token)
    return _guard(cases.admin_get, case_id)


@app.post("/api/admin/cases/{case_id}/status")
def admin_status(case_id: str, u: StatusUpdate, x_admin_token: str = Header(default="")) -> dict:
    _admin(x_admin_token)
    _guard(cases.admin_set_status, case_id, u.status, u.note)
    return {"ok": True}


@app.get("/api/admin/cases/{case_id}/evidence/{evidence_id}")
def admin_evidence(case_id: str, evidence_id: str, x_admin_token: str = Header(default="")) -> FileResponse:
    _admin(x_admin_token)
    path, name, ctype = _guard(cases.admin_file, case_id, evidence_id)
    return FileResponse(path, filename=name, media_type=ctype or "application/octet-stream")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
