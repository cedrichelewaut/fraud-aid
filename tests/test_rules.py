"""Run with: venv/bin/python tests/test_rules.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.assess import Facts, decide


def facts(**kw):
    base = dict(
        understood="x",
        payment_authorised_by_victim="unclear",
        how="other",
        impersonated="unknown",
        shared_credentials="unclear",
    )
    return Facts(**{**base, **kw})


cases = [
    (dict(payment_authorised_by_victim="no"), "strong"),
    (dict(how="phishing_link", payment_authorised_by_victim="unclear"), "strong"),
    (dict(how="phone_call", payment_authorised_by_victim="yes", impersonated="bank"), "possible"),
    (dict(how="investment", payment_authorised_by_victim="yes", impersonated="none"), "unlikely"),
    (dict(), "unclear"),
]
for kw, want in cases:
    got = decide(facts(**kw)).level
    assert got == want, (kw, got, want)

v = decide(facts(payment_authorised_by_victim="no", amount_eur=500), amount_override=10000)
assert v.up_to_eur == 10000
assert decide(facts(payment_authorised_by_victim="yes"), 10000).up_to_eur is None
print("rules ok")
