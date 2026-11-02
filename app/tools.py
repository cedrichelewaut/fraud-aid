"""Static content and document builders: tips, claim letter, police report, waitlist."""

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

TIPS = {
    "phone_calls": [
        "Hang up, then call your bank on the number on your card. Do not use a number the caller gives you.",
        "Caller ID can be faked, so a familiar number proves nothing.",
        "Banks and police never ask you to approve transfers or hand over codes by phone.",
        "Your bank will never ask you to move money to a safe account.",
    ],
    "messages_and_links": [
        "Do not click links in messages about parcels, fines or bank problems. Open the app or site yourself.",
        "Forward suspicious messages to verdacht@safeonweb.be.",
        "Check the sender address and web address letter by letter.",
        "Never share itsme approvals, Digipass codes or card details, even with someone who knows your name.",
    ],
    "elderly_relatives": [
        "Agree a family code word, so a call from a relative in trouble can be checked.",
        "Help them set a low transfer limit in the banking app and turn on payment alerts.",
        "Tell them it is fine to hang up on anyone, and that they can always call you first.",
        "Remind them that urgency is the scammer's tool. A real problem can wait ten minutes.",
    ],
    "investments": [
        "Guaranteed returns do not exist. Be wary of anyone who found you through social media or a messaging app.",
        "Check the company on the FSMA warning list (fsma.be) before sending money.",
        "Be careful with anyone offering to recover lost investments for an upfront fee. That is a common second scam.",
    ],
    "marketplaces": [
        "Do not pay by bank transfer to people you do not know. Use the platform's own payment protection.",
        "Never click payment links a buyer sends you. Buyers do not need your card or itsme to pay you.",
        "If a price is too good to be true, ask for a video call with the item before paying.",
    ],
    "your_accounts": [
        "Lower the transfer limit in your banking app so one mistake cannot empty your account.",
        "Turn on payment notifications so you see every movement at once.",
        "Use a different password for every account and a password manager.",
        "Never let anyone control your computer or phone remotely, even if they say they are from support.",
    ],
}

LETTERS = {
    "en": {
        "subject": "Fraud claim and request for immediate refund",
        "unauth": "On {date} an amount of EUR {amount} left my account without my approval. {story}\n\nUnder the Belgian rules on payment services (PSD2), you must refund an unauthorised payment immediately. If you believe I was grossly negligent, it is for you to prove that after refunding me.",
        "auth": "On {date} I transferred EUR {amount} after being deceived by a fraudster. {story}\n\nI ask you to (1) contact the receiving bank immediately to recall or freeze the funds, (2) investigate this case, and (3) reimburse me. I reserve all my rights, including under the new EU payment rules and before Ombudsfin.",
        "close": "Please confirm receipt and reply in writing within 10 days. I have reported or will report this to the police.",
        "hello": "Dear Sir or Madam,",
        "bye": "Kind regards,",
        "ref": "Account (IBAN): [your IBAN]",
    },
    "nl": {
        "subject": "Fraudeclaim en verzoek tot onmiddellijke terugbetaling",
        "unauth": "Op {date} is een bedrag van EUR {amount} zonder mijn toestemming van mijn rekening gegaan. {story}\n\nVolgens de Belgische regels voor betalingsdiensten (PSD2) moet u een niet-toegestane betaling onmiddellijk terugbetalen. Indien u meent dat ik grof nalatig was, dient u dat na de terugbetaling zelf te bewijzen.",
        "auth": "Op {date} heb ik EUR {amount} overgemaakt nadat een fraudeur mij had misleid. {story}\n\nIk verzoek u (1) onmiddellijk contact op te nemen met de ontvangende bank om de gelden terug te halen of te blokkeren, (2) dit dossier te onderzoeken en (3) mij terug te betalen. Ik behoud al mijn rechten, ook onder de nieuwe Europese betaalregels en bij Ombudsfin.",
        "close": "Gelieve de ontvangst te bevestigen en binnen 10 dagen schriftelijk te antwoorden. Ik heb dit gemeld of zal dit melden bij de politie.",
        "hello": "Geachte heer, mevrouw,",
        "bye": "Met vriendelijke groeten,",
        "ref": "Rekening (IBAN): [uw IBAN]",
    },
    "fr": {
        "subject": "Réclamation pour fraude et demande de remboursement immédiat",
        "unauth": "Le {date}, un montant de {amount} EUR a quitté mon compte sans mon autorisation. {story}\n\nEn vertu des règles belges sur les services de paiement (PSD2), vous devez rembourser immédiatement une opération non autorisée. Si vous estimez que j'ai commis une négligence grave, il vous appartient de le prouver après m'avoir remboursé.",
        "auth": "Le {date}, j'ai viré {amount} EUR après avoir été trompé par un fraudeur. {story}\n\nJe vous demande (1) de contacter immédiatement la banque destinataire afin de rappeler ou bloquer les fonds, (2) d'examiner ce dossier et (3) de me rembourser. Je me réserve tous mes droits, y compris au titre des nouvelles règles européennes en matière de paiement et auprès d'Ombudsfin.",
        "close": "Veuillez accuser réception et répondre par écrit dans les 10 jours. J'ai signalé ou je signalerai ces faits à la police.",
        "hello": "Madame, Monsieur,",
        "bye": "Cordialement,",
        "ref": "Compte (IBAN) : [votre IBAN]",
    },
}

POLICE = {
    "en": {
        "title": "Report of online fraud",
        "labels": ("Date", "Amount lost", "Bank", "How I paid", "How it started", "I approved the payment myself", "Scammer details", "Account of events"),
        "how": {"phone_call": "Phone call", "phishing_link": "Text, email or link (phishing)", "messaging": "Message on WhatsApp or social media", "investment": "Investment scam", "marketplace": "Online purchase or sale", "romance": "Romance or person in need", "other": "Other"},
        "method": {"transfer": "Bank transfer", "card": "Card payment", "both": "Bank transfer and card", "other": "Other"},
        "tri": {"yes": "yes, under false pretences", "no": "no", "unclear": "not sure"},
        "unknown": "[IBAN, phone number, website or profile, if known]",
    },
    "nl": {
        "title": "Aangifte van online oplichting",
        "labels": ("Datum", "Verloren bedrag", "Bank", "Hoe ik betaalde", "Hoe het begon", "Ik keurde de betaling zelf goed", "Gegevens van de oplichter", "Feiten"),
        "how": {"phone_call": "Telefoongesprek", "phishing_link": "Sms, e-mail of link (phishing)", "messaging": "Bericht via WhatsApp of sociale media", "investment": "Beleggingsfraude", "marketplace": "Online aankoop of verkoop", "romance": "Romance of persoon in nood", "other": "Andere"},
        "method": {"transfer": "Overschrijving", "card": "Kaartbetaling", "both": "Overschrijving en kaart", "other": "Andere"},
        "tri": {"yes": "ja, onder valse voorwendselen", "no": "nee", "unclear": "niet zeker"},
        "unknown": "[IBAN, telefoonnummer, website of profiel, indien gekend]",
    },
    "fr": {
        "title": "Déclaration d'escroquerie en ligne",
        "labels": ("Date", "Montant perdu", "Banque", "Mode de paiement", "Début des faits", "J'ai approuvé le paiement moi-même", "Données de l'escroc", "Faits"),
        "how": {"phone_call": "Appel téléphonique", "phishing_link": "SMS, e-mail ou lien (hameçonnage)", "messaging": "Message WhatsApp ou réseaux sociaux", "investment": "Fraude à l'investissement", "marketplace": "Achat ou vente en ligne", "romance": "Romance ou personne en détresse", "other": "Autre"},
        "method": {"transfer": "Virement", "card": "Paiement par carte", "both": "Virement et carte", "other": "Autre"},
        "tri": {"yes": "oui, sous de faux prétextes", "no": "non", "unclear": "pas sûr"},
        "unknown": "[IBAN, numéro de téléphone, site web ou profil, si connu]",
    },
}

FALLBACK_STORY = {
    "en": "I was the victim of a scam ({how}). I lost EUR {amount}.",
    "nl": "Ik ben het slachtoffer van oplichting ({how}). Ik verloor EUR {amount}.",
    "fr": "J'ai été victime d'une escroquerie ({how}). J'ai perdu {amount} EUR.",
}

DATA = Path(os.getenv("FRAUD_AID_DATA") or Path(__file__).resolve().parent.parent / "data")


def lang_of(v) -> str:
    return v if v in LETTERS else "en"


def money(amount: Optional[float], lang: str) -> str:
    if not amount:
        return "[amount]"
    n = f"{amount:,.0f}"
    return n if lang_of(lang) == "en" else n.replace(",", ".")


def date_text(when: str) -> str:
    return date.today().isoformat() if when == "today" else "[date]"


def build_letter(bank: str, amount: Optional[float], story: str, authorised: str, when: str, lang: str) -> str:
    t = LETTERS[lang_of(lang)]
    body = (t["unauth"] if authorised == "no" else t["auth"]).format(
        date=date_text(when), amount=money(amount, lang), story=story.strip()
    )
    return "\n\n".join([bank, t["subject"], t["hello"], body, t["ref"], t["close"], t["bye"], "[your name]", f"[{date.today().isoformat()}]"])


def build_police_report(a, story: str) -> str:
    """`a` is an Answers object (see app/plan.py)."""
    t = POLICE[lang_of(a.language)]
    L = t["labels"]
    amount = f"EUR {money(a.amount_eur, a.language)}" if a.amount_eur else "[amount]"
    lines = [
        t["title"],
        "",
        f"{L[0]}: {date_text(a.when)}",
        f"{L[1]}: {amount}",
        f"{L[2]}: {a.bank}",
        f"{L[3]}: {t['method'][a.method]}",
        f"{L[4]}: {t['how'][a.how]}",
        f"{L[5]}: {t['tri'][a.authorised]}",
        f"{L[6]}: {a.scammer_details.strip() or t['unknown']}",
        "",
        f"{L[7]}:",
        story.strip(),
    ]
    return "\n".join(lines)


def save_waitlist(email: str, country: Optional[str] = None, note: Optional[str] = None) -> None:
    DATA.mkdir(exist_ok=True)
    row = {"email": email, "country": country, "note": note, "at": datetime.now(timezone.utc).isoformat()}
    with open(DATA / "waitlist.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
