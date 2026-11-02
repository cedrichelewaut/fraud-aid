"""Plan builder, no LLM. Run with: venv/bin/python tests/test_plan.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.plan import Answers, build_plan


def answers(**kw):
    base = dict(how="phone_call", impersonated="bank", authorised="yes", method="transfer", when="today", bank="KBC", amount_eur=10000)
    return Answers(**{**base, **kw})


def ids(plan):
    return [s.id for s in plan.steps]


# Order is fixed: Card Stop, police, bank, claim, protect
p = build_plan(answers(), "I was called.")
assert ids(p) == ["cardstop", "police", "bank", "claim", "protect"], ids(p)
assert p.urgent and p.verdict.level == "possible" and p.verdict.up_to_eur == 10000 and p.can_offer_help
assert p.steps[0].actions[0].href == "tel:078170170"
assert "KBC" in p.steps[2].title
assert p.steps[1].doc and "EUR 10.000" in p.steps[1].doc.text
assert p.steps[2].doc and "KBC" in p.steps[2].doc.text

# Not approved: strong, English letter uses the unauthorised wording
p = build_plan(answers(authorised="no", how="phishing_link", impersonated=None, language="en"), "x")
assert p.verdict.level == "strong"
assert "without my approval" in p.steps[2].doc.text and "EUR 10,000" in p.steps[2].doc.text

# Approved investment scam: unlikely, no amount, no help offer, FSMA mentioned
p = build_plan(answers(how="investment", impersonated=None, when="older"), "x")
assert p.verdict.level == "unlikely" and p.verdict.up_to_eur is None and not p.can_offer_help and not p.urgent
assert any("FSMA" in b for b in p.steps[1].bullets)

# Remote access and shared credentials show up in the protect step
p = build_plan(answers(remote_access="yes", shared_credentials="yes", method="card", told_bank=True, told_police=True), "x")
text = " ".join(p.steps[4].bullets)
assert "AnyDesk" in text and "itsme" in text
assert any("chargeback" in b for b in p.steps[2].bullets)
assert "already reported" in p.steps[1].bullets[0]

# Unknown amount does not break the documents
p = build_plan(answers(amount_eur=None), "x")
assert "[amount]" in p.steps[2].doc.text and p.verdict.up_to_eur is None

# French police report
p = build_plan(answers(language="fr"), "x")
assert "Déclaration" in p.steps[1].doc.text
# Cents are kept in the documents, in each language's number format
p = build_plan(answers(amount_eur=1234.5, language="nl"), "x")
assert "EUR 1.234,50" in p.steps[2].doc.text and "EUR 1.234,50" in p.steps[1].doc.text
p = build_plan(answers(amount_eur=444.5, language="en"), "x")
assert "EUR 444.50" in p.steps[2].doc.text
p = build_plan(answers(amount_eur=444, language="fr"), "x")
assert "444 EUR" in p.steps[2].doc.text
# The statement from the model is cleaned: one plain paragraph, no titles, markdown or second version
from app.plan import clean_statement
messy = "**Déclaration pour la banque :**\n\nJ'ai reçu un SMS avec un lien. J'ai saisi mes données.\n\n---\n\n**Déclaration pour la police :**\n\nJ'ai été victime d'une usurpation."
assert clean_statement(messy) == "J'ai reçu un SMS avec un lien. J'ai saisi mes données.", clean_statement(messy)
assert clean_statement("# Titel\n- Ik werd gebeld.\n- Ik betaalde zelf.") == "Ik werd gebeld. Ik betaalde zelf."
assert len(clean_statement("Een zin. " * 400)) <= 901

# The plan text follows the interface language
for lang, title, headline in [("en", "Call Card Stop", "Probably entitled to a refund"), ("fr", "Appelez Card Stop", "Droit probable à un remboursement"), ("nl", "Bel Card Stop", "Waarschijnlijk recht op terugbetaling")]:
    p = build_plan(answers(authorised="no", how="phishing_link", impersonated=None, ui=lang), "x")
    assert p.steps[0].title == title and p.verdict.headline == headline, (lang, p.steps[0].title, p.verdict.headline)
    assert len(p.steps) == 5 and all(s.title for s in p.steps)
# and the document language is independent of it
p = build_plan(answers(ui="fr", language="nl"), "x")
assert "Appelez" in p.steps[2].title and "Geachte" in p.steps[2].doc.text
print("plan ok")
