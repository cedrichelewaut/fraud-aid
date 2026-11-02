"""Verdict rules. The LLM never decides entitlement: `decide` does, from the answers the user clicked.

Rules and wording are a placeholder until a Belgian lawyer reviews them.
"""

from typing import Literal, Optional

from pydantic import BaseModel

from .i18n import BASIS, HEADLINES, pick

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


def decide(facts: Facts, amount_override: Optional[float] = None, lang: str = "en") -> Verdict:
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
        headline=pick(HEADLINES, lang)[level],
        up_to_eur=up_to,
        basis=pick(BASIS, lang)[level],
    )
