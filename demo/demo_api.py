"""Runs the real Fraud Aid backend inside the browser (Pyodide) for the static demo.

`handle()` mirrors the routes in app/main.py. No network: the AI statement step falls back
to the user's own words, and cases live in this browser only (IndexedDB).
"""

import json
import os
import sys
import types

os.environ.setdefault("FRAUD_AID_DATA", "/data")
os.environ.setdefault("FRAUD_AID_ADMIN_TOKEN", "demo")

# No outbound HTTP in the demo: make the optional model call fail, so the fallback is used.
httpx = types.ModuleType("httpx")


class HTTPError(Exception):
    pass


class AsyncClient:
    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, *a, **k):
        raise HTTPError("no model in the demo")


httpx.HTTPError = HTTPError
httpx.AsyncClient = AsyncClient
sys.modules.setdefault("httpx", httpx)

# The e-mail validator package is not needed in the demo; the form already checks the address.
import pydantic  # noqa: E402

pydantic.EmailStr = str

import hmac  # noqa: E402

from pydantic import ValidationError  # noqa: E402

from app import cases  # noqa: E402
from app.i18n import LANGS, TIPS, pick  # noqa: E402
from app.plan import Answers, build_plan, summarize  # noqa: E402


class Http(Exception):
    def __init__(self, status, detail):
        self.status, self.detail = status, detail


def _guard(fn, *args):
    try:
        return fn(*args)
    except cases.NotFound:
        raise Http(404, "Case not found.")
    except cases.Forbidden:
        raise Http(403, "Wrong or missing case token.")
    except cases.BadUpload as e:
        raise Http(400, str(e))
    except cases.NotEligible as e:
        raise Http(422, str(e))


def _admin(headers):
    if not hmac.compare_digest("demo", headers.get("x-admin-token", "")):
        raise Http(403, "Wrong admin token. In the demo it is: demo")


def _lang(q):
    v = q.get("lang", "en")
    return v if v in LANGS else "en"


async def _route(method, path, q, headers, body, file):
    parts = path.strip("/").split("/")[1:]  # drop "api"
    if parts == ["tips"]:
        return pick(TIPS, _lang(q))
    if parts == ["terms"]:
        return cases.terms(_lang(q))
    if parts == ["health"]:
        return {"ok": True}
    if parts == ["waitlist"]:
        return {"ok": True}  # nothing is stored in the demo
    if parts == ["plan"]:
        a = Answers.model_validate(body)
        summary = (a.summary or "").strip() or await summarize(a)
        return build_plan(a, summary).model_dump()
    if parts == ["verdict"]:
        p = build_plan(Answers.model_validate(body), "")
        return {"level": p.verdict.level, "can_offer_help": p.can_offer_help}
    if parts == ["cases"] and method == "POST":
        case_id, token = _guard(cases.create_case, cases.CaseCreate.model_validate(body))
        return {"case_id": case_id, "token": token}
    if parts[0] == "cases" and len(parts) == 2:
        tok = headers.get("x-case-token", "")
        if method == "GET":
            return _guard(cases.victim_view, parts[1], tok)
        if method == "DELETE":
            _guard(cases.delete_case, parts[1], tok)
            return {"deleted": True}
    if parts[0] == "cases" and len(parts) == 3 and parts[2] == "evidence" and method == "POST":
        name, ctype, data = file
        if len(data) > cases.MAX_BYTES:
            raise Http(400, "File too large.")
        return _guard(cases.add_evidence, parts[1], headers.get("x-case-token", ""), name, ctype, data)
    if parts[0] == "admin":
        _admin(headers)
        if parts[1:] == ["cases"]:
            return cases.admin_list()
        if len(parts) == 3 and parts[1] == "cases":
            return _guard(cases.admin_get, parts[2])
        if len(parts) == 4 and parts[3] == "status" and method == "POST":
            _guard(cases.admin_set_status, parts[2], body["status"], (body.get("note") or "")[:300])
            return {"ok": True}
        if len(parts) == 5 and parts[3] == "evidence":
            path_, name, ctype = _guard(cases.admin_file, parts[2], parts[4])
            return {"__file__": str(path_), "name": name, "type": ctype or "application/octet-stream"}
    raise Http(404, "Not found.")


async def handle(method, path, query_json, headers_json, body_json, file_name, file_type, file_bytes):
    """Returns (status, json_text) or (200, '__file__' marker handled in JS)."""
    q = json.loads(query_json or "{}")
    headers = {k.lower(): v for k, v in json.loads(headers_json or "{}").items()}
    body = json.loads(body_json) if body_json else None
    try:
        out = await _route(method, path, q, headers, body, (file_name, file_type, bytes(file_bytes or b"")))
        return 200, json.dumps(out, default=str)
    except Http as e:
        return e.status, json.dumps({"detail": e.detail})
    except ValidationError as e:
        return 422, json.dumps({"detail": json.loads(e.json())})
