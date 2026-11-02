from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from .plan import Answers, Plan, build_plan, summarize
from .tools import TIPS, save_waitlist

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Fraud Aid")


class WaitlistRequest(BaseModel):
    email: EmailStr
    consent: bool
    country: Optional[str] = None
    note: Optional[str] = None


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/tips")
def tips() -> dict:
    return TIPS


@app.post("/api/plan", response_model=Plan)
async def plan(a: Answers) -> Plan:
    # Answers are used to build the response and are never logged or stored.
    return build_plan(a, await summarize(a))


@app.post("/api/waitlist")
def waitlist(req: WaitlistRequest) -> dict:
    if not req.consent:
        raise HTTPException(400, "Consent is required.")
    save_waitlist(req.email, (req.country or "")[:40] or None, (req.note or "")[:200] or None)
    return {"ok": True}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
