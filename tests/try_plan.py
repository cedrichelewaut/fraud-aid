"""Live check of POST /api/plan (uses the local model for the summary): venv/bin/python tests/try_plan.py"""
import time

import httpx

body = {
    "country": "BE", "amount_eur": 10000, "how": "phone_call", "impersonated": "bank", "authorised": "yes",
    "method": "transfer", "when": "today", "bank": "KBC", "shared_credentials": "no", "remote_access": "no",
    "told_bank": False, "told_police": False, "scammer_details": "BE68 5390 0754 7034",
    "free_text": "A man called from the fraud team of my bank and said my account was hacked. He told me to move my savings to a safe account. I approved it in the app this morning.",
    "language": "nl",
}
t = time.time()
r = httpx.post("http://localhost:8000/api/plan", json=body, timeout=300)
print(r.status_code, f"{time.time() - t:.1f}s")
p = r.json()
print(p["verdict"]["level"], p["verdict"]["up_to_eur"], "urgent:", p["urgent"])
print("SUMMARY:", p["summary"], "\n")
for s in p["steps"]:
    print(f"- {s['id']}: {s['title']}  ({len(s['bullets'])} bullets, doc={bool(s['doc'])})")
print("\n" + p["steps"][1]["doc"]["text"])
