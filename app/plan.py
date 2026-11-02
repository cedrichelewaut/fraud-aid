"""Builds the action plan from the answers the user clicked.

Everything the user relies on (verdict, steps, letter, police text) is deterministic.
The local LLM only rewrites the user's own words into a short, factual first-person
statement for the documents, and the result is shown for the user to check.
"""

import os
from typing import Literal, Optional

import httpx
from pydantic import BaseModel, Field

from .assess import Facts, Verdict, decide
from .i18n import PLAN, pick
from .tools import FALLBACK_STORY, POLICE, build_letter, build_police_report, lang_of, money

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("FRAUD_AID_MODEL", "ministral-3:8b")

Tri = Literal["yes", "no", "unclear"]
How = Literal["phone_call", "phishing_link", "messaging", "marketplace", "investment", "romance", "other"]


class Answers(BaseModel):
    country: Literal["BE"] = "BE"
    amount_eur: Optional[float] = Field(default=None, gt=0, lt=10_000_000)
    how: How
    free_text: str = Field(default="", max_length=3000)
    impersonated: Optional[Literal["bank", "police", "company", "relative", "none"]] = None
    authorised: Tri
    method: Literal["transfer", "card", "both", "other"]
    when: Literal["today", "last_3_days", "last_month", "older"]
    bank: str = Field(min_length=1, max_length=60)
    shared_credentials: Tri = "unclear"
    remote_access: Tri = "unclear"
    told_bank: bool = False
    told_police: bool = False
    scammer_details: str = Field(default="", max_length=500)
    language: Literal["en", "nl", "fr"] = "nl"  # language of the documents
    ui: Literal["en", "nl", "fr"] = "en"  # language of the plan text
    summary: Optional[str] = Field(default=None, max_length=3000)  # reuse a statement already written


class Action(BaseModel):
    label: str
    href: str


class Doc(BaseModel):
    title: str
    text: str


class Step(BaseModel):
    id: str
    title: str
    intro: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    doc: Optional[Doc] = None


class Plan(BaseModel):
    urgent: bool
    verdict: Verdict
    steps: list[Step]
    summary: str
    can_offer_help: bool


LANG_NAME = {"en": "English", "nl": "Dutch", "fr": "French"}


def clean_statement(text: str) -> str:
    """The model sometimes adds titles, markdown or a second version. Keep one plain paragraph."""
    text = text.replace("**", "").replace("__", "").split("---")[0]
    kept = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if len(line) <= 70 and line.endswith(":") or line.endswith(" :"):
            continue  # a heading such as "Statement for the bank:"
        kept.append(line.lstrip("-*\u2022 ").strip())
    out = " ".join(" ".join(kept).split())
    if len(out) > 900:  # cut at the last full sentence
        cut = out[:900]
        out = cut[: max(cut.rfind(". "), cut.rfind("."))] + "." if "." in cut else cut
    return out


async def summarize(a: Answers) -> str:
    """First-person factual statement in the document language. Falls back to the user's own words."""
    lang = lang_of(a.language)
    how = POLICE[lang]["how"][a.how]
    fallback = a.free_text.strip() or FALLBACK_STORY[lang].format(how=how, amount=money(a.amount_eur, lang))
    facts = [
        f"How it started: {POLICE['en']['how'][a.how]}",
        f"Pretended to be: {a.impersonated}" if a.impersonated else None,
        f"Amount lost: EUR {money(a.amount_eur, 'en')}" if a.amount_eur else None,
        f"Paid by: {POLICE['en']['method'][a.method]}",
        f"Approved the payment themselves: {a.authorised}",
    ]
    facts_text = "\n".join(f"- {f}" for f in facts if f)
    prompt = (
        f"Write a short factual statement of 3 to 5 sentences in {LANG_NAME[lang]}, in the first person, "
        "for a bank and the police. Use only the facts and the account below. Do not add names, numbers, dates, denials or any detail that is not given, "
        "and do not mention what was not said. No opinions, no legal claims, no greetings. Write exactly one paragraph of plain text of at most 4 sentences: say each thing once, do not repeat yourself, and do not add consequences that are not stated (for example that an account was emptied). No title, no markdown, no list and no second version. Output only that paragraph.\n\n"
        f"Facts:\n{facts_text}\n\nUser's own account (may be empty):\n<account>\n{a.free_text.strip()}\n</account>"
    )
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 0.1},
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
        text = clean_statement(r.json()["message"]["content"])
        return text if len(text) > 20 else fallback
    except (httpx.HTTPError, KeyError, ValueError):
        return fallback


def build_plan(a: Answers, summary: str) -> Plan:
    L = pick(PLAN, a.ui)
    facts = Facts(
        payment_authorised_by_victim=a.authorised,
        how=a.how,
        impersonated=a.impersonated or "unknown",
        shared_credentials=a.shared_credentials,
        amount_eur=a.amount_eur,
    )
    v = decide(facts, lang=a.ui)
    bank = a.bank if a.bank and a.bank.lower() != "other" else L["bank_fallback"]
    urgent = a.when in ("today", "last_3_days")
    cards_involved = a.method in ("card", "both") or a.shared_credentials == "yes"

    steps: list[Step] = []

    # 1. Card Stop
    steps.append(
        Step(
            id="cardstop",
            title=L["cardstop_title"],
            intro=[L["cardstop_cards"] if cards_involved else L["cardstop_other"]],
            actions=[Action(label=L["cardstop_call"], href="tel:078170170")],
        )
    )

    # 2. Police
    police_bullets = []
    if a.told_police:
        police_bullets.append(L["police_already"])
    police_bullets += [L["police_online"], L["police_inperson"], L["police_safeonweb"]]
    if a.how == "investment":
        police_bullets.append(L["police_fsma"])
    if a.how == "marketplace":
        police_bullets.append(L["police_platform"])
    steps.append(
        Step(
            id="police",
            title=L["police_title"],
            intro=[L["police_intro"]],
            bullets=police_bullets,
            actions=[Action(label=L["police_action"], href="https://www.policeonweb.be")],
            doc=Doc(title=L["police_doc"], text=build_police_report(a, summary)),
        )
    )

    # 3. Bank
    bank_bullets = [L["bank_b1"], L["bank_b2"], L["bank_b3"]]
    if a.method in ("card", "both"):
        bank_bullets.append(L["bank_card"])
    if a.told_bank:
        bank_bullets.insert(0, L["bank_told"])
    if urgent:
        bank_bullets.append(L["bank_urgent"])
    steps.append(
        Step(
            id="bank",
            title=L["bank_title"].format(bank=bank),
            intro=[L["bank_intro"]],
            bullets=bank_bullets,
            doc=Doc(title=L["bank_doc"], text=build_letter(a.bank, a.amount_eur, summary, a.authorised, a.when, a.language)),
        )
    )

    # 4. Claim back
    steps.append(
        Step(
            id="claim",
            title=L["claim_title"],
            intro=[L[f"{v.level}_intro"]],
            bullets=[L[k] for k in sorted(L) if k.startswith(f"{v.level}_") and k[len(v.level) + 1:].isdigit()],
            actions=[Action(label=L["claim_action"], href="https://www.ombudsfin.be")],
        )
    )

    # 5. Protect
    protect = []
    if a.remote_access == "yes":
        protect.append(L["protect_remote"])
    if a.shared_credentials == "yes":
        protect.append(L["protect_codes"])
    protect += [L["protect_watch"], L["protect_recovery"], L["protect_family"]]
    steps.append(Step(id="protect", title=L["protect_title"], bullets=protect))

    return Plan(
        urgent=urgent,
        verdict=v,
        steps=steps,
        summary=summary,
        can_offer_help=v.level in ("strong", "possible"),
    )
