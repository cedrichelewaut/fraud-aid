"""Paid-tier prototype: cases, evidence, status, back office, deletion. No LLM needed.
Run with: venv/bin/python tests/test_cases.py"""
import os
import sys
import tempfile
from pathlib import Path

tmp = tempfile.mkdtemp()
os.environ["FRAUD_AID_DATA"] = tmp
os.environ["FRAUD_AID_ADMIN_TOKEN"] = "admin-secret"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.cases import iban_ok
from app.main import app

c = TestClient(app)

assert iban_ok("BE68 5390 0754 7034") and iban_ok("NL91ABNA0417164300")
assert not iban_ok("BE68 5390 0754 7035") and not iban_ok("hello")

answers = dict(how="phone_call", impersonated="bank", authorised="no", method="transfer", when="today", bank="KBC", amount_eur=5000)
contact = dict(full_name="Jeff Peeters", email="jeff@example.com", phone="+32 470 00 00 00", address="Kerkstraat 1, 9000 Gent", iban="BE68 5390 0754 7034")
consent = dict(privacy=True, terms=True, mandate=True, signature_name="Jeff Peeters", share_intel=True)
body = dict(answers=answers, summary="I was called by someone pretending to be my bank.", contact=contact, consent=consent)

# Missing consent is refused
bad = {**body, "consent": {**consent, "mandate": False}}
assert c.post("/api/cases", json=bad).status_code == 422
# Invalid IBAN is refused
assert c.post("/api/cases", json={**body, "contact": {**contact, "iban": "BE00 0000 0000 0000"}}).status_code == 422
# A case we would decline (approved investment scam) is refused
declined = {**body, "answers": {**answers, "how": "investment", "impersonated": None, "authorised": "yes"}}
assert c.post("/api/cases", json=declined).status_code == 422

# Create
r = c.post("/api/cases", json=body)
assert r.status_code == 200, r.text
case_id, token = r.json()["case_id"], r.json()["token"]
assert case_id.startswith("FA-") and len(token) > 20
H = {"X-Case-Token": token}

# Victim view needs the token
assert c.get(f"/api/cases/{case_id}").status_code == 403
assert c.get(f"/api/cases/{case_id}", headers={"X-Case-Token": "nope"}).status_code == 403
assert c.get("/api/cases/FA-NOPE00", headers=H).status_code == 404
v = c.get(f"/api/cases/{case_id}", headers=H).json()
assert v["status"] == "received" and "iban" not in v and "email" not in v

# Evidence: allowed, wrong type, wrong token
ok = c.post(f"/api/cases/{case_id}/evidence", headers=H, files={"file": ("statement.pdf", b"%PDF-1.4 test", "application/pdf")})
assert ok.status_code == 200, ok.text
assert c.post(f"/api/cases/{case_id}/evidence", headers=H, files={"file": ("virus.exe", b"MZ", "application/octet-stream")}).status_code == 400
assert c.post(f"/api/cases/{case_id}/evidence", headers={"X-Case-Token": "x"}, files={"file": ("a.pdf", b"x", "application/pdf")}).status_code == 403
assert c.post(f"/api/cases/{case_id}/evidence", headers=H, files={"file": ("../../etc/passwd.pdf", b"x", "application/pdf")}).status_code == 200
files = c.get(f"/api/cases/{case_id}", headers=H).json()["files"]
assert [f["original_name"] for f in files] == ["statement.pdf", "passwd.pdf"], files
assert len(list((Path(tmp) / "evidence" / case_id).iterdir())) == 2

# Back office
A = {"X-Admin-Token": "admin-secret"}
assert c.get("/api/admin/cases").status_code == 403
assert c.get("/api/admin/cases", headers={"X-Admin-Token": "wrong"}).status_code == 403
lst = c.get("/api/admin/cases", headers=A).json()
assert lst[0]["id"] == case_id and lst[0]["bank"] == "KBC" and lst[0]["amount"] == 5000 and lst[0]["files"] == 2
d = c.get(f"/api/admin/cases/{case_id}", headers=A).json()
assert d["iban"] == "BE68539007547034" and d["share_intel"] is True and len(d["docs"]) == 2 and "token_hash" not in d
assert c.post(f"/api/admin/cases/{case_id}/status", headers=A, json={"status": "claim_sent", "note": "Sent to KBC"}).status_code == 200
assert c.post(f"/api/admin/cases/{case_id}/status", headers=A, json={"status": "bogus"}).status_code == 400
v = c.get(f"/api/cases/{case_id}", headers=H).json()
assert v["status"] == "claim_sent" and v["events"][-1]["note"] == "Sent to KBC"
eid = d["files"][0]["id"]
assert c.get(f"/api/admin/cases/{case_id}/evidence/{eid}", headers=A).content == b"%PDF-1.4 test"

# Terms and tips come in all three languages
for lang, word in [("en", "Draft terms"), ("fr", "Conditions provisoires"), ("nl", "Voorlopige voorwaarden")]:
    assert word in c.get(f"/api/terms?lang={lang}").json()["draft_notice"]
assert c.get("/api/terms?lang=xx").json()["draft_notice"].startswith("Draft")  # unknown language falls back to English
tips = {l: c.get(f"/api/tips?lang={l}").json() for l in ("en", "fr", "nl")}
assert list(tips["en"]) == list(tips["fr"]) == list(tips["nl"]) and "zero_trust" in tips["en"]
assert all(len(tips[l][k]["items"]) == len(tips["en"][k]["items"]) and tips[l][k]["intro"] for l in tips for k in tips[l])
assert "tells" in tips["en"]["zero_trust"]["items"][0]["h"] and tips["fr"]["zero_trust"]["items"][6]["h"] == "Allez sur place"

# Quick check of whether Fraud Aid can take a case, without the AI step
ok_case = dict(how="phone_call", impersonated="bank", authorised="yes", method="transfer", when="today", bank="KBC", amount_eur=500)
assert c.post("/api/verdict", json=ok_case).json() == {"level": "possible", "can_offer_help": True}
assert c.post("/api/verdict", json={**ok_case, "how": "investment", "impersonated": None}).json() == {"level": "unlikely", "can_offer_help": False}

# A status change without a note is stored as a code, so the victim reads it in their own language
assert c.post(f"/api/admin/cases/{case_id}/status", headers=A, json={"status": "won", "note": ""}).status_code == 200
ev = c.get(f"/api/cases/{case_id}", headers=H).json()["events"]
assert ev[-1]["note"] == "status:won" and ev[-1]["kind"] == "status" and ev[0]["kind"] == "created"

# Erasure removes the row, the events and the files
assert c.delete(f"/api/cases/{case_id}", headers={"X-Case-Token": "x"}).status_code == 403
assert c.delete(f"/api/cases/{case_id}", headers=H).json() == {"deleted": True}
assert c.get(f"/api/cases/{case_id}", headers=H).status_code == 404
assert not (Path(tmp) / "evidence" / case_id).exists()
assert c.get("/api/admin/cases", headers=A).json() == []

# Back office is off without a token configured
os.environ["FRAUD_AID_ADMIN_TOKEN"] = ""
assert c.get("/api/admin/cases", headers=A).status_code == 403
print("cases ok")
