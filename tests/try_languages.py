"""Live check: the plan in each interface language, with the AI statement in each document language.
Run with the server up: venv/bin/python tests/try_languages.py"""
import httpx

base = dict(country="BE", amount_eur=4200, how="phishing_link", authorised="no", method="transfer", when="today", bank="Belfius",
            shared_credentials="yes", remote_access="no", told_bank=False, told_police=False)
text = {"fr": "J'ai reçu un SMS de ma banque avec un lien et saisi mes données. 4200 euros ont disparu.",
        "nl": "Ik kreeg een sms van mijn bank met een link en vulde mijn gegevens in. Er verdween 4200 euro.",
        "en": "I got a text from my bank with a link and entered my details. 4200 euros disappeared."}
for doc_lang in ("fr", "nl", "en"):
    r = httpx.post("http://localhost:8000/api/plan", json={**base, "language": doc_lang, "ui": doc_lang, "free_text": text[doc_lang]}, timeout=300)
    p = r.json()
    s = p["summary"]
    print(f"[{doc_lang}] {p['steps'][0]['title']} | {p['verdict']['headline']}\n     statement: {s}")
    assert "**" not in s and "---" not in s and "\n" not in s, "statement not clean"
print("clean statements ok")
