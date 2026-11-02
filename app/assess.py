"""Verdict rules. The LLM never decides entitlement: `decide` does, from the answers the user clicked.

Rules and wording are a placeholder until a Belgian lawyer reviews them.
"""

from typing import Literal, Optional

from pydantic import BaseModel

Tri = Literal["yes", "no", "unclear"]


class Facts(BaseModel):
    payment_authorised_by_victim: Tri = "unclear"
    how: Literal["phishing_link", "phone_call", "messaging", "marketplace", "investment", "romance", "other"] = "other"
    impersonated: Literal["bank", "police", "company", "relative", "none", "unknown"] = "unknown"
    shared_credentials: Tri = "unclear"
    amount_eur: Optional[float] = None
    hours_since: Optional[float] = None


class Verdict(BaseModel):
    level: Literal["strong", "possible", "unlikely", "unclear"]
    headline: str
    up_to_eur: Optional[float]
    basis: str


BASIS = {
    "strong": (
        "When a payment was not approved by you, Belgian payment law (PSD2) requires the bank to refund it "
        "promptly. The bank can only recover the money from you later if it proves gross negligence, and "
        "recent Belgian and EU court rulings read that test strictly."
    ),
    "possible": (
        "You approved the payment, so the bank is not automatically liable today. New EU rules (PSD3 and PSR, "
        "politically agreed in November 2025) are set to make banks refund victims of bank impersonation. "
        "Until they apply, success depends on the details and on how the bank and the ombudsman see your case."
    ),
    "unlikely": (
        "You approved the payment yourself, and current Belgian law generally does not make the bank refund "
        "payments a customer authorised, even when they were tricked. Acting fast can still help: the "
        "receiving bank can sometimes freeze what is left."
    ),
    "unclear": "More details are needed before it is clear where the person stands.",
}

HEADLINES = {
    "strong": "Probably entitled to a refund",
    "possible": "May have a claim",
    "unlikely": "A refund is unlikely under current rules",
    "unclear": "More information needed",
}


def decide(facts: Facts, amount_override: Optional[float] = None) -> Verdict:
    authorised = facts.payment_authorised_by_victim
    if facts.how == "phishing_link" and authorised != "yes":
        level = "strong"
    elif authorised == "no":
        level = "strong"
    elif authorised == "yes" and facts.impersonated == "bank":
        level = "possible"
    elif authorised == "yes":
        level = "unlikely"
    else:
        level = "unclear"

    amount = amount_override if amount_override else facts.amount_eur
    up_to = amount if level in ("strong", "possible") else None

    return Verdict(
        level=level,
        headline=HEADLINES[level],
        up_to_eur=up_to,
        basis=BASIS[level],
    )
