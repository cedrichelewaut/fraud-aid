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
    language: Literal["en", "nl", "fr"] = "nl"


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


async def summarize(a: Answers) -> str:
    """First-person factual statement in the document language. Falls back to the user's own words."""
    lang = lang_of(a.language)
    how = POLICE[lang]["how"][a.how]
    fallback = a.free_text.strip() or FALLBACK_STORY[lang].format(how=how, amount=money(a.amount_eur, lang))
    facts = [
        f"How it started: {POLICE['en']['how'][a.how]}",
        f"Pretended to be: {a.impersonated}" if a.impersonated else None,
        f"Amount lost: EUR {a.amount_eur:,.0f}" if a.amount_eur else None,
        f"Paid by: {POLICE['en']['method'][a.method]}",
        f"Approved the payment themselves: {a.authorised}",
    ]
    facts_text = "\n".join(f"- {f}" for f in facts if f)
    prompt = (
        f"Write a short factual statement of 3 to 5 sentences in {LANG_NAME[lang]}, in the first person, "
        "for a bank and the police. Use only the facts and the account below. Do not add names, numbers, dates, denials or any detail that is not given, "
        "and do not mention what was not said. No opinions, no legal claims, no greetings. Output only the statement.\n\n"
        f"Facts:\n{facts_text}\n\nUser's own account (may be empty):\n<account>\n{a.free_text.strip()}\n</account>"
    )
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 0.2},
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
        text = r.json()["message"]["content"].strip()
        return text if len(text) > 20 else fallback
    except (httpx.HTTPError, KeyError, ValueError):
        return fallback


def build_plan(a: Answers, summary: str) -> Plan:
    facts = Facts(
        payment_authorised_by_victim=a.authorised,
        how=a.how,
        impersonated=a.impersonated or "unknown",
        shared_credentials=a.shared_credentials,
        amount_eur=a.amount_eur,
    )
    v = decide(facts)
    bank = a.bank if a.bank and a.bank.lower() != "other" else "your bank"
    urgent = a.when in ("today", "last_3_days")
    cards_involved = a.method in ("card", "both") or a.shared_credentials == "yes"

    steps: list[Step] = []

    # 1. Card Stop
    steps.append(
        Step(
            id="cardstop",
            title="Call Card Stop",
            intro=[
                "Block your bank cards first. Card Stop is reachable around the clock, and it takes a couple of minutes."
                if cards_involved
                else "Your cards may not be at risk, but blocking them is the fastest way to be safe while you sort out the rest. Your bank can reissue them."
            ],
            actions=[Action(label="Call 078 170 170", href="tel:078170170")],
        )
    )

    # 2. Police
    police_bullets = []
    if a.told_police:
        police_bullets.append("You said you already reported this. Keep the reference number and add anything below that is missing.")
    police_bullets += [
        "Online: policeonweb.be, where it is available for your type of fraud. You receive a reference number.",
        "In person: go to your local police station. Bring your ID, your phone and the report text below, and ask them to register an official complaint. Keep the reference number or a copy of your statement.",
        "Forward suspicious messages and websites to verdacht@safeonweb.be.",
    ]
    if a.how == "investment":
        police_bullets.append("Investment scams: also tell the FSMA (fsma.be), which publishes warnings about fraudulent firms.")
    if a.how == "marketplace":
        police_bullets.append("Report the listing or profile to the platform with its report function so others are not caught.")
    steps.append(
        Step(
            id="police",
            title="Report it to the police",
            intro=["Your bank, the ombudsman and any refund claim will ask for the police report, so do this today."],
            bullets=police_bullets,
            actions=[Action(label="Open Police on Web", href="https://www.policeonweb.be")],
            doc=Doc(title="Report text for the police", text=build_police_report(a, summary)),
        )
    )

    # 3. Bank
    bank_bullets = [
        "Say it is fraud and ask them to block your online banking access and reset your itsme or Digipass.",
        "Ask them to recall or freeze the payment and to contact the receiving bank straight away.",
        "Ask them to open a fraud case, give you the case reference and confirm everything in writing.",
    ]
    if a.method in ("card", "both"):
        bank_bullets.append("For the card payment, ask for a chargeback dispute. Card schemes only allow a limited window, so ask on day one.")
    if a.told_bank:
        bank_bullets.insert(0, "You said you already told your bank. Ask for the case reference and send the written claim below anyway.")
    if urgent:
        bank_bullets.append("It just happened, so speed matters: money that has not left the receiving account yet can sometimes be frozen.")
    steps.append(
        Step(
            id="bank",
            title=f"Call {bank} and send a written claim",
            intro=["Use the number on the back of your card or in your banking app, never a number the scammer gave you."],
            bullets=bank_bullets,
            doc=Doc(title="Written claim to your bank", text=build_letter(a.bank, a.amount_eur, summary, a.authorised, a.when, a.language)),
        )
    )

    # 4. Claim back
    if v.level == "strong":
        claim_intro = [
            "From your answers, you did not approve this payment. Belgian payment law (PSD2) says the bank must refund unauthorised payments promptly, and it can only recover the money from you later if it proves gross negligence. Belgian and EU courts read that test strictly."
        ]
        claim_bullets = [
            "Report the problem to your bank without delay, and within 13 months of the payment at the latest.",
            "Send the written claim by email and by registered post, and keep the proofs.",
            "Mention that you have reported it to the police and ask for the refund in writing.",
            "If the bank refuses or does not answer within a few weeks, file a free complaint with Ombudsfin. A refusal is not the end: Belgian courts have ordered banks to refund immediately.",
        ]
    elif v.level == "possible":
        claim_intro = [
            "You approved the payment, so the bank is not automatically liable today. EU rules that are set to make banks refund victims of bank impersonation (PSD3 and PSR) were politically agreed in November 2025 but are not in force yet. Success depends on the details."
        ]
        claim_bullets = [
            "Send the written claim and ask for reimbursement and for the payment to be recalled.",
            "Keep every message, call log and screenshot. They are your evidence.",
            "If the bank refuses, file a free complaint with Ombudsfin and ask for the decision in writing.",
            "Keep your file complete, because the new rules may change how banks must treat cases like yours.",
        ]
    elif v.level == "unlikely":
        claim_intro = [
            "You approved the payment yourself, and current Belgian law generally does not oblige the bank to refund it, even when you were tricked. You still have options."
        ]
        claim_bullets = [
            "Send the written claim and ask the bank to contact the receiving bank about the payment.",
            "Ask the bank to consider a goodwill refund and request the answer in writing.",
            "File a free complaint with Ombudsfin if the bank says no.",
            "If you have legal expenses insurance, ask whether it covers a lawyer's opinion.",
        ]
    else:
        claim_intro = ["We need to know whether you approved the payment yourself before we can say where you stand."]
        claim_bullets = [
            "Send the written claim anyway and ask the bank to investigate and recall the payment.",
            "If the bank refuses, file a free complaint with Ombudsfin.",
        ]
    steps.append(
        Step(
            id="claim",
            title="Claim your money back",
            intro=claim_intro,
            bullets=claim_bullets,
            actions=[Action(label="Ombudsfin", href="https://www.ombudsfin.be")],
        )
    )

    # 5. Protect
    protect = []
    if a.remote_access == "yes":
        protect.append("Disconnect the device from the internet, remove any remote access app (AnyDesk, TeamViewer and similar) and change your passwords from another device. Consider a professional check or a factory reset.")
    if a.shared_credentials == "yes":
        protect.append("You shared codes or card details. Change your passwords, reset itsme or Digipass and ask for replacement cards.")
    protect += [
        "Watch your accounts closely for the next weeks and turn on payment notifications.",
        "Do not pay anyone who offers to recover your money for a fee. That is a second scam, and victims are often targeted twice.",
        "Warn your family. Scammers often come back or move on to relatives.",
    ]
    steps.append(Step(id="protect", title="Protect yourself now", bullets=protect))

    return Plan(
        urgent=urgent,
        verdict=v,
        steps=steps,
        summary=summary,
        can_offer_help=v.level in ("strong", "possible"),
    )
