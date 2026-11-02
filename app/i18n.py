"""Server-side text in English, French and Dutch: verdicts, plan steps, fee terms and tips.

The wording is a first translation and needs review by a native-speaking Belgian lawyer
together with the English originals.
"""

LANGS = ("en", "fr", "nl")


def pick(table: dict, lang: str):
    return table.get(lang) or table["en"]


HEADLINES = {
    "en": {
        "strong": "Probably entitled to a refund",
        "possible": "May have a claim",
        "unlikely": "A refund is unlikely under current rules",
        "unclear": "More information needed",
    },
    "fr": {
        "strong": "Droit probable à un remboursement",
        "possible": "Réclamation possible",
        "unlikely": "Remboursement peu probable selon les règles actuelles",
        "unclear": "Informations complémentaires nécessaires",
    },
    "nl": {
        "strong": "Waarschijnlijk recht op terugbetaling",
        "possible": "Mogelijk een claim",
        "unlikely": "Terugbetaling onwaarschijnlijk volgens de huidige regels",
        "unclear": "Meer informatie nodig",
    },
}

BASIS = {
    "en": {
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
    },
    "fr": {
        "strong": (
            "Lorsqu'un paiement n'a pas été approuvé par vous, la loi belge sur les services de paiement (PSD2) impose "
            "à la banque de le rembourser rapidement. La banque ne peut récupérer l'argent auprès de vous par la suite "
            "que si elle prouve une négligence grave, et la jurisprudence belge et européenne récente applique ce "
            "critère strictement."
        ),
        "possible": (
            "Vous avez approuvé le paiement, la banque n'est donc pas automatiquement responsable aujourd'hui. De "
            "nouvelles règles européennes (PSD3 et PSR, convenues politiquement en novembre 2025) devraient obliger "
            "les banques à rembourser les victimes d'usurpation d'identité bancaire. D'ici leur entrée en vigueur, le "
            "résultat dépend des détails et de l'appréciation de la banque et du médiateur."
        ),
        "unlikely": (
            "Vous avez approuvé le paiement vous-même, et le droit belge actuel n'oblige en général pas la banque à "
            "rembourser des paiements autorisés par le client, même quand il a été trompé. Agir vite peut quand même "
            "aider : la banque destinataire peut parfois bloquer ce qui reste."
        ),
        "unclear": "Il faut davantage de détails avant de pouvoir dire où en est la personne.",
    },
    "nl": {
        "strong": (
            "Wanneer een betaling niet door jou is goedgekeurd, verplicht de Belgische betaalwetgeving (PSD2) de bank "
            "om die snel terug te betalen. De bank kan het geld pas later bij jou terugvorderen als ze grove "
            "nalatigheid bewijst, en recente Belgische en Europese rechtspraak past die toets streng toe."
        ),
        "possible": (
            "Je hebt de betaling goedgekeurd, dus de bank is vandaag niet automatisch aansprakelijk. Nieuwe Europese "
            "regels (PSD3 en PSR, politiek overeengekomen in november 2025) moeten banken verplichten slachtoffers van "
            "bankimitatie terug te betalen. Tot ze van kracht zijn, hangt het resultaat af van de details en van hoe "
            "de bank en de ombudsman je zaak zien."
        ),
        "unlikely": (
            "Je hebt de betaling zelf goedgekeurd en het huidige Belgische recht verplicht de bank er in het algemeen "
            "niet toe betalingen terug te betalen die de klant heeft goedgekeurd, ook als hij of zij is bedrogen. "
            "Snel handelen kan toch helpen: de ontvangende bank kan soms bevriezen wat er nog over is."
        ),
        "unclear": "Er zijn meer details nodig voordat duidelijk is waar de persoon staat.",
    },
}

PLAN = {
    "en": {
        "cardstop_title": "Call Card Stop",
        "cardstop_cards": "Block your bank cards first. Card Stop is reachable around the clock, and it takes a couple of minutes.",
        "cardstop_other": "Your cards may not be at risk, but blocking them is the fastest way to be safe while you sort out the rest. Your bank can reissue them.",
        "cardstop_call": "Call 078 170 170",
        "police_title": "Report it to the police",
        "police_intro": "Your bank, the ombudsman and any refund claim will ask for the police report, so do this today.",
        "police_already": "You said you already reported this. Keep the reference number and add anything below that is missing.",
        "police_online": "Online: policeonweb.be, where it is available for your type of fraud. You receive a reference number.",
        "police_inperson": "In person: go to your local police station. Bring your ID, your phone and the report text below, and ask them to register an official complaint. Keep the reference number or a copy of your statement.",
        "police_safeonweb": "Forward suspicious messages and websites to verdacht@safeonweb.be.",
        "police_fsma": "Investment scams: also tell the FSMA (fsma.be), which publishes warnings about fraudulent firms.",
        "police_platform": "Report the listing or profile to the platform with its report function so others are not caught.",
        "police_action": "Open Police on Web",
        "police_doc": "Report text for the police",
        "bank_title": "Call {bank} and send a written claim",
        "bank_fallback": "your bank",
        "bank_intro": "Use the number on the back of your card or in your banking app, never a number the scammer gave you.",
        "bank_b1": "Say it is fraud and ask them to block your online banking access and reset your itsme or Digipass.",
        "bank_b2": "Ask them to recall or freeze the payment and to contact the receiving bank straight away.",
        "bank_b3": "Ask them to open a fraud case, give you the case reference and confirm everything in writing.",
        "bank_card": "For the card payment, ask for a chargeback dispute. Card schemes only allow a limited window, so ask on day one.",
        "bank_told": "You said you already told your bank. Ask for the case reference and send the written claim below anyway.",
        "bank_urgent": "It just happened, so speed matters: money that has not left the receiving account yet can sometimes be frozen.",
        "bank_doc": "Written claim to your bank",
        "claim_title": "Claim your money back",
        "claim_action": "Ombudsfin",
        "strong_intro": "From your answers, you did not approve this payment. Belgian payment law (PSD2) says the bank must refund unauthorised payments promptly, and it can only recover the money from you later if it proves gross negligence. Belgian and EU courts read that test strictly.",
        "strong_1": "Report the problem to your bank without delay, and within 13 months of the payment at the latest.",
        "strong_2": "Send the written claim by email and by registered post, and keep the proofs.",
        "strong_3": "Mention that you have reported it to the police and ask for the refund in writing.",
        "strong_4": "If the bank refuses or does not answer within a few weeks, file a free complaint with Ombudsfin. A refusal is not the end: Belgian courts have ordered banks to refund immediately.",
        "possible_intro": "You approved the payment, so the bank is not automatically liable today. EU rules that are set to make banks refund victims of bank impersonation (PSD3 and PSR) were politically agreed in November 2025 but are not in force yet. Success depends on the details.",
        "possible_1": "Send the written claim and ask for reimbursement and for the payment to be recalled.",
        "possible_2": "Keep every message, call log and screenshot. They are your evidence.",
        "possible_3": "If the bank refuses, file a free complaint with Ombudsfin and ask for the decision in writing.",
        "possible_4": "Keep your file complete, because the new rules may change how banks must treat cases like yours.",
        "unlikely_intro": "You approved the payment yourself, and current Belgian law generally does not oblige the bank to refund it, even when you were tricked. You still have options.",
        "unlikely_1": "Send the written claim and ask the bank to contact the receiving bank about the payment.",
        "unlikely_2": "Ask the bank to consider a goodwill refund and request the answer in writing.",
        "unlikely_3": "File a free complaint with Ombudsfin if the bank says no.",
        "unlikely_4": "If you have legal expenses insurance, ask whether it covers a lawyer's opinion.",
        "unclear_intro": "We need to know whether you approved the payment yourself before we can say where you stand.",
        "unclear_1": "Send the written claim anyway and ask the bank to investigate and recall the payment.",
        "unclear_2": "If the bank refuses, file a free complaint with Ombudsfin.",
        "protect_title": "Protect yourself now",
        "protect_remote": "Disconnect the device from the internet, remove any remote access app (AnyDesk, TeamViewer and similar) and change your passwords from another device. Consider a professional check or a factory reset.",
        "protect_codes": "You shared codes or card details. Change your passwords, reset itsme or Digipass and ask for replacement cards.",
        "protect_watch": "Watch your accounts closely for the next weeks and turn on payment notifications.",
        "protect_recovery": "Do not pay anyone who offers to recover your money for a fee. That is a second scam, and victims are often targeted twice.",
        "protect_family": "Warn your family. Scammers often come back or move on to relatives.",
    },
    "fr": {
        "cardstop_title": "Appelez Card Stop",
        "cardstop_cards": "Bloquez d'abord vos cartes bancaires. Card Stop est joignable jour et nuit et cela ne prend que quelques minutes.",
        "cardstop_other": "Vos cartes ne sont peut-être pas en danger, mais les bloquer est le moyen le plus rapide d'être tranquille pendant que vous réglez le reste. Votre banque peut vous en refaire.",
        "cardstop_call": "Appeler le 078 170 170",
        "police_title": "Déposez plainte à la police",
        "police_intro": "Votre banque, le médiateur et toute demande de remboursement vous demanderont le rapport de police, faites-le donc aujourd'hui.",
        "police_already": "Vous avez dit avoir déjà déclaré les faits. Gardez le numéro de référence et complétez avec ce qui manque ci-dessous.",
        "police_online": "En ligne : policeonweb.be, lorsque c'est possible pour votre type de fraude. Vous recevez un numéro de référence.",
        "police_inperson": "En personne : rendez-vous au commissariat de votre commune. Apportez votre carte d'identité, votre téléphone et le texte ci-dessous, et demandez qu'on enregistre une plainte officielle. Gardez le numéro de référence ou une copie de votre déposition.",
        "police_safeonweb": "Transférez les messages et sites suspects à verdacht@safeonweb.be.",
        "police_fsma": "Fraudes à l'investissement : informez aussi la FSMA (fsma.be), qui publie des avertissements sur les sociétés frauduleuses.",
        "police_platform": "Signalez l'annonce ou le profil à la plateforme via sa fonction de signalement, pour que d'autres ne se fassent pas piéger.",
        "police_action": "Ouvrir Police on Web",
        "police_doc": "Texte pour la police",
        "bank_title": "Appelez {bank} et envoyez une réclamation écrite",
        "bank_fallback": "votre banque",
        "bank_intro": "Utilisez le numéro au dos de votre carte ou dans votre application bancaire, jamais un numéro donné par l'escroc.",
        "bank_b1": "Dites qu'il s'agit d'une fraude et demandez de bloquer votre accès aux services bancaires en ligne et de réinitialiser votre itsme ou Digipass.",
        "bank_b2": "Demandez de rappeler ou de bloquer le paiement et de contacter immédiatement la banque destinataire.",
        "bank_b3": "Demandez l'ouverture d'un dossier de fraude, la référence du dossier et une confirmation écrite de tout.",
        "bank_card": "Pour le paiement par carte, demandez une procédure de rétrofacturation (chargeback). Les réseaux de cartes n'accordent qu'un délai limité, demandez-la dès le premier jour.",
        "bank_told": "Vous avez dit avoir déjà prévenu votre banque. Demandez la référence du dossier et envoyez quand même la réclamation écrite ci-dessous.",
        "bank_urgent": "C'est tout récent, donc la rapidité compte : l'argent qui n'a pas encore quitté le compte destinataire peut parfois être bloqué.",
        "bank_doc": "Réclamation écrite à votre banque",
        "claim_title": "Réclamez votre argent",
        "claim_action": "Ombudsfin",
        "strong_intro": "D'après vos réponses, vous n'avez pas approuvé ce paiement. La loi belge sur les services de paiement (PSD2) impose à la banque de rembourser rapidement les paiements non autorisés, et elle ne peut récupérer l'argent auprès de vous par la suite que si elle prouve une négligence grave. Les tribunaux belges et européens appliquent ce critère strictement.",
        "strong_1": "Signalez le problème à votre banque sans tarder, et au plus tard dans les 13 mois suivant le paiement.",
        "strong_2": "Envoyez la réclamation écrite par e-mail et par courrier recommandé, et gardez les preuves.",
        "strong_3": "Mentionnez que vous avez déposé plainte et demandez le remboursement par écrit.",
        "strong_4": "Si la banque refuse ou ne répond pas dans les quelques semaines, déposez gratuitement une plainte auprès d'Ombudsfin. Un refus n'est pas la fin : des tribunaux belges ont ordonné à des banques de rembourser immédiatement.",
        "possible_intro": "Vous avez approuvé le paiement, la banque n'est donc pas automatiquement responsable aujourd'hui. Les règles européennes destinées à obliger les banques à rembourser les victimes d'usurpation d'identité bancaire (PSD3 et PSR) ont fait l'objet d'un accord politique en novembre 2025 mais ne sont pas encore en vigueur. Le résultat dépend des détails.",
        "possible_1": "Envoyez la réclamation écrite et demandez le remboursement ainsi que le rappel du paiement.",
        "possible_2": "Gardez chaque message, journal d'appels et capture d'écran. Ce sont vos preuves.",
        "possible_3": "Si la banque refuse, déposez gratuitement une plainte auprès d'Ombudsfin et demandez la décision par écrit.",
        "possible_4": "Gardez votre dossier complet, car les nouvelles règles pourraient changer la façon dont les banques doivent traiter les cas comme le vôtre.",
        "unlikely_intro": "Vous avez approuvé le paiement vous-même, et le droit belge actuel n'oblige en général pas la banque à le rembourser, même si vous avez été trompé. Vous avez quand même des options.",
        "unlikely_1": "Envoyez la réclamation écrite et demandez à la banque de contacter la banque destinataire au sujet du paiement.",
        "unlikely_2": "Demandez à la banque d'envisager un remboursement à titre gracieux et exigez la réponse par écrit.",
        "unlikely_3": "Déposez gratuitement une plainte auprès d'Ombudsfin si la banque refuse.",
        "unlikely_4": "Si vous avez une assurance protection juridique, demandez si elle couvre l'avis d'un avocat.",
        "unclear_intro": "Nous devons savoir si vous avez approuvé le paiement vous-même avant de pouvoir dire où vous en êtes.",
        "unclear_1": "Envoyez quand même la réclamation écrite et demandez à la banque d'enquêter et de rappeler le paiement.",
        "unclear_2": "Si la banque refuse, déposez gratuitement une plainte auprès d'Ombudsfin.",
        "protect_title": "Protégez-vous maintenant",
        "protect_remote": "Déconnectez l'appareil d'internet, supprimez toute application d'accès à distance (AnyDesk, TeamViewer et similaires) et changez vos mots de passe depuis un autre appareil. Envisagez un contrôle par un professionnel ou une réinitialisation d'usine.",
        "protect_codes": "Vous avez communiqué des codes ou des données de carte. Changez vos mots de passe, réinitialisez itsme ou Digipass et demandez des cartes de remplacement.",
        "protect_watch": "Surveillez vos comptes de près dans les semaines à venir et activez les notifications de paiement.",
        "protect_recovery": "Ne payez personne qui propose de récupérer votre argent contre rémunération. C'est une deuxième arnaque, et les victimes sont souvent visées deux fois.",
        "protect_family": "Prévenez votre famille. Les escrocs reviennent souvent ou s'attaquent aux proches.",
    },
    "nl": {
        "cardstop_title": "Bel Card Stop",
        "cardstop_cards": "Blokkeer eerst je bankkaarten. Card Stop is dag en nacht bereikbaar en het duurt maar een paar minuten.",
        "cardstop_other": "Je kaarten lopen misschien geen gevaar, maar ze blokkeren is de snelste manier om veilig te zijn terwijl je de rest regelt. Je bank kan nieuwe kaarten aanmaken.",
        "cardstop_call": "Bel 078 170 170",
        "police_title": "Doe aangifte bij de politie",
        "police_intro": "Je bank, de ombudsman en elke terugbetalingsaanvraag zullen om het proces-verbaal vragen, doe dit dus vandaag nog.",
        "police_already": "Je zei dat je dit al hebt aangegeven. Bewaar het referentienummer en vul aan wat hieronder ontbreekt.",
        "police_online": "Online: policeonweb.be, waar dat mogelijk is voor jouw soort fraude. Je krijgt een referentienummer.",
        "police_inperson": "Persoonlijk: ga naar je lokale politiekantoor. Neem je identiteitskaart, je telefoon en de tekst hieronder mee en vraag om een officiële klacht te laten registreren. Bewaar het referentienummer of een kopie van je verklaring.",
        "police_safeonweb": "Stuur verdachte berichten en websites door naar verdacht@safeonweb.be.",
        "police_fsma": "Beleggingsfraude: meld het ook aan de FSMA (fsma.be), die waarschuwingen over frauduleuze bedrijven publiceert.",
        "police_platform": "Meld de advertentie of het profiel bij het platform via de meldfunctie, zodat anderen er niet intrappen.",
        "police_action": "Open Police on Web",
        "police_doc": "Tekst voor de politie",
        "bank_title": "Bel {bank} en stuur een schriftelijke claim",
        "bank_fallback": "je bank",
        "bank_intro": "Gebruik het nummer op de achterkant van je kaart of in je bankapp, nooit een nummer dat de oplichter je gaf.",
        "bank_b1": "Zeg dat het om fraude gaat en vraag om je toegang tot online bankieren te blokkeren en je itsme of Digipass opnieuw in te stellen.",
        "bank_b2": "Vraag om de betaling terug te halen of te bevriezen en meteen contact op te nemen met de ontvangende bank.",
        "bank_b3": "Vraag om een fraudedossier te openen, je het dossiernummer te geven en alles schriftelijk te bevestigen.",
        "bank_card": "Vraag voor de kaartbetaling een chargeback (terugboeking) aan. Kaartnetwerken geven maar beperkte tijd, vraag het dus meteen.",
        "bank_told": "Je zei dat je je bank al hebt verwittigd. Vraag het dossiernummer en stuur toch de schriftelijke claim hieronder.",
        "bank_urgent": "Het is net gebeurd, dus snelheid telt: geld dat de ontvangende rekening nog niet heeft verlaten kan soms worden bevroren.",
        "bank_doc": "Schriftelijke claim aan je bank",
        "claim_title": "Eis je geld terug",
        "claim_action": "Ombudsfin",
        "strong_intro": "Volgens je antwoorden heb je deze betaling niet goedgekeurd. De Belgische betaalwetgeving (PSD2) bepaalt dat de bank niet-toegestane betalingen snel moet terugbetalen en het geld pas later bij jou kan terugvorderen als ze grove nalatigheid bewijst. Belgische en Europese rechtbanken passen die toets streng toe.",
        "strong_1": "Meld het probleem zonder uitstel aan je bank, en uiterlijk binnen 13 maanden na de betaling.",
        "strong_2": "Stuur de schriftelijke claim per e-mail en per aangetekende post en bewaar de bewijzen.",
        "strong_3": "Vermeld dat je aangifte hebt gedaan en vraag de terugbetaling schriftelijk.",
        "strong_4": "Als de bank weigert of binnen enkele weken niet antwoordt, dien dan gratis een klacht in bij Ombudsfin. Een weigering is niet het einde: Belgische rechtbanken hebben banken bevolen onmiddellijk terug te betalen.",
        "possible_intro": "Je hebt de betaling goedgekeurd, dus de bank is vandaag niet automatisch aansprakelijk. De Europese regels die banken moeten verplichten slachtoffers van bankimitatie terug te betalen (PSD3 en PSR) zijn in november 2025 politiek overeengekomen maar nog niet van kracht. Het resultaat hangt van de details af.",
        "possible_1": "Stuur de schriftelijke claim en vraag om terugbetaling en om de betaling terug te halen.",
        "possible_2": "Bewaar elk bericht, elke oproeplog en elke screenshot. Het zijn je bewijzen.",
        "possible_3": "Als de bank weigert, dien dan gratis een klacht in bij Ombudsfin en vraag de beslissing schriftelijk.",
        "possible_4": "Houd je dossier compleet, want de nieuwe regels kunnen veranderen hoe banken zaken zoals de jouwe moeten behandelen.",
        "unlikely_intro": "Je hebt de betaling zelf goedgekeurd en het huidige Belgische recht verplicht de bank er in het algemeen niet toe die terug te betalen, ook niet als je bent bedrogen. Je hebt toch nog opties.",
        "unlikely_1": "Stuur de schriftelijke claim en vraag de bank contact op te nemen met de ontvangende bank over de betaling.",
        "unlikely_2": "Vraag de bank een terugbetaling uit coulance te overwegen en vraag het antwoord schriftelijk.",
        "unlikely_3": "Dien gratis een klacht in bij Ombudsfin als de bank nee zegt.",
        "unlikely_4": "Als je een rechtsbijstandverzekering hebt, vraag dan of die het advies van een advocaat dekt.",
        "unclear_intro": "We moeten weten of je de betaling zelf hebt goedgekeurd voordat we kunnen zeggen waar je staat.",
        "unclear_1": "Stuur de schriftelijke claim toch en vraag de bank de zaak te onderzoeken en de betaling terug te halen.",
        "unclear_2": "Als de bank weigert, dien dan gratis een klacht in bij Ombudsfin.",
        "protect_title": "Bescherm jezelf nu",
        "protect_remote": "Koppel het toestel los van internet, verwijder elke app voor toegang op afstand (AnyDesk, TeamViewer en dergelijke) en wijzig je wachtwoorden vanaf een ander toestel. Overweeg een controle door een specialist of een fabrieksreset.",
        "protect_codes": "Je deelde codes of kaartgegevens. Wijzig je wachtwoorden, stel itsme of Digipass opnieuw in en vraag vervangende kaarten aan.",
        "protect_watch": "Houd je rekeningen de komende weken goed in de gaten en schakel betalingsmeldingen in.",
        "protect_recovery": "Betaal niemand die aanbiedt je geld tegen betaling terug te halen. Dat is een tweede oplichting en slachtoffers worden vaak twee keer geviseerd.",
        "protect_family": "Waarschuw je familie. Oplichters komen vaak terug of richten zich op familieleden.",
    },
}

def _t(intro, *items):
    return {"intro": intro, "items": [{"h": h, "p": p} for h, p in items]}


TIPS = {
    "en": {
        "zero_trust": _t(
            "Modern fraud does not look like fraud. The people behind it are professionals who test what works, so the old warning signs are unreliable. Treat every unexpected contact as unverified, however real it feels, and verify it yourself through a channel you control.",
            ("There are no reliable tells", "Typos, rushing, threats and strange accents belong to the cheap scams. The skilled ones are polite, patient and well prepared. Some deliberately show no urgency at all, because a calm person who says 'take your time' feels trustworthy. Some even say 'hang up and call your bank' and then control what happens next. Judge what is being asked, never how it is asked."),
            ("Knowing things about you proves nothing", "Your name, address, bank, recent payments and family members can come from data breaches, earlier scams, public registers and social media. A caller or message that knows them is not more likely to be real."),
            ("Verify through a channel you choose", "Never use a number, link, address or name that the other person gave you to check them. Look up the real number on your card or in an official letter, type the web address yourself, or open the app yourself. A real number on your screen proves nothing either: numbers and sender names can be faked."),
            ("A voice or a face is not proof", "With a few seconds of recorded speech, AI can copy the voice of your mother, your father or your child, and live video can be faked too. A familiar voice on the phone, even crying or in distress, is no longer evidence that it is them. Agree a code word in person, and read the topic on family, voices and video."),
            ("Watch what is asked, not who asks", "Stop whenever someone asks you to send money, move it to a 'safe' account, read out or approve a code, install an app, share your screen or change a limit. A real bank, police officer or company has no need for any of these. Whatever the voice, the logo or the story, the answer is no."),
            ("If you are not 100% sure, do nothing risky", "No transfer, no code, no app, no new payee, until you have checked. Waiting a day costs you nothing, and a real problem will still be there. No pressure does not mean it is safe: showing no urgency is also a technique."),
            ("Go in person", "There is no harm in walking into your bank's branch with your phone or laptop and asking whether something is real. Nobody will think you are foolish; staff are glad when customers check. Find the address yourself on your card, your statement or the bank's own website, and ask them to look at your account and show you what is safe."),
            ("Talk to someone you trust first", "Before any large or unusual payment, tell a person you trust and listen to their doubts. Fraudsters often ask for secrecy ('the bank is involved', 'do not tell the staff'). Any instruction to hide something from people who care about you is a reason to tell them."),
            ("Make the damage smaller", "Lower your transfer limit in your banking app, turn on payment notifications, keep savings in a separate account that is not in your everyday app, and use a delay or a second approval for new payees where your bank offers it."),
            ("Being fooled is not being foolish", "These operations are run like businesses, with scripts, research and teams. Careful, intelligent people are caught every day. If it happens to you, act quickly and tell someone: it protects you and others."),
        ),
        "phone_calls": _t(
            "Phone fraud has moved on from the clumsy caller. Today's callers can seem calm, helpful and perfectly informed. Use the rules below even when everything feels right.",
            ("The number on your screen can be faked", "A call can show your bank's real number, or appear in the same list as earlier genuine calls. The display proves nothing. The same goes for a voice message or a text that arrives right after the call."),
            ("A calm caller is not a safe caller", "Some fraudsters rush you. The better ones are patient, warm and in no hurry. They may even say you can hang up and call the bank yourself, so that you feel in control. Then they steer what follows: a number they gave you, a second 'colleague' who answers, or a call that never really ended. Decide on your own, with your own steps."),
            ("How to check properly", "End the call. Wait a few minutes, or use a different phone if you can. Then look up the number yourself, on the back of your card or on the bank's official website that you typed in, and ask whether the call was real. Better still, go to a branch."),
            ("What a real bank never asks", "Moving money to protect it, approving or cancelling a payment in the app on their instruction, installing an app, sharing your screen, reading out codes or itsme approvals, or giving card details. If any of these is requested it is fraud, however convincing the person is."),
            ("Do not say yes and do not press anything", "Short answers such as 'yes' can be recorded and reused. If a call feels wrong, say nothing more and end it."),
            ("Offers of help are suspect", "Calls from 'technical support', 'the police', 'the tax office' or 'a fraud team' that you did not ask for are the way in. Real organisations write to you or let you contact them."),
            ("Tell someone", "Say out loud what is being asked, to a person you trust. Scammers rely on you being alone with the call."),
        ),
        "messages_and_links": _t(
            "Phishing is now well written, well designed and often impossible to tell apart from the real thing. Do not rely on spotting it: change how you act.",
            ("Never log in through a link", "Whatever the message says, open your bank's app or type its web address yourself. Fake sites copy logos, wording and even live chat perfectly. A single changed letter in the address is often the only difference."),
            ("The same thread proves nothing", "Fraudulent texts can appear in the same conversation as your bank's real messages, and fake emails can show the correct sender name. A message that appears in the right place is not proof."),
            ("Perfect language is normal now", "AI writes flawless Dutch, French and English. The absence of typos tells you nothing."),
            ("Read what you approve", "An itsme or banking-app request that you did not start yourself is a warning. Read the amount, the recipient and the action on the screen before you confirm. Do not approve a request just because it looks routine."),
            ("QR codes and attachments are links too", "A QR code, a PDF, a payment request or a 'delivery' notice can lead to the same fake pages. The same goes for messages saying you received a refund or sent a payment by mistake."),
            ("Report them", "Forward suspicious messages to verdacht@safeonweb.be and delete them. Do not reply, not even to say stop."),
        ),
        "family_voices": _t(
            "A call or video from someone you love can now be fake. A few seconds of their voice, taken from a social media video or a voicemail, is enough to copy it, with their tone, accent and way of speaking. Plan for this before it happens.",
            ("Voices can be cloned", "Scammers can imitate your child, partner, parent or grandchild and say they are in trouble: an accident, an arrest, a lost phone, a new number. It can sound exactly like them, even crying. A familiar voice is no longer proof."),
            ("Video is not proof either", "Live video can be faked or altered too. A video call showing a known face is better than a voice, but it is still not certain, especially when something odd or urgent is asked."),
            ("Agree a code word, in person", "Choose a word or question together, face to face, that nobody could find online: not a pet's name or a birthplace. Never write it or say it in messages. Change it after it has been used. Ask for it whenever money or secrets are involved."),
            ("Break the loop", "Hang up. Call the person back on the number you already have, or call someone who is with them. If you cannot reach them, ask a relative, visit, or wait. A real emergency survives a few minutes of checking."),
            ("Be wary of any request for money", "Transfers to a new account, gift cards, crypto, cash handed to a courier, or a new phone number 'because mine broke' are classics. So is being asked to keep it secret."),
            ("Help parents and grandparents", "Talk about this calmly, not as a lecture. Agree that they will always call you before any unusual payment, however convincing the caller, and that hanging up is always fine. Help them lower their transfer limit and turn on payment alerts, and check in regularly."),
            ("Limit what is public", "The more of your voice and your family's details are public, the easier they are to copy. Keep social media private where you can, and avoid openly posting voice clips of children and elderly relatives."),
        ),
        "investments": _t(
            "Investment fraud is slow and patient. The people behind it often spend weeks on you before they ask for much.",
            ("Trust is built over time", "It can start as friendship or romance on a messaging app, or as a helpful 'adviser'. They show impressive but plausible gains, share screenshots and sometimes let you withdraw a small sum. A first payout proves nothing: it is bait."),
            ("Check the firm yourself", "Look the company up on the FSMA register and its warning list (fsma.be). Scammers copy the names, licence numbers and websites of real firms, so check that the website, address and phone number match the official register, which you found yourself."),
            ("Be wary of guarantees and 'inside tips'", "No one can guarantee returns. Modest returns can be a lie just like huge ones. Anyone steering you to a platform you cannot visit, or to crypto transfers you do not understand, deserves extra distrust."),
            ("Slow down and ask", "Tell a trusted person, ask an independent adviser, and ask your bank in person. If your bank warns you about a payment, take the warning seriously, even if the other person told you the bank is wrong."),
            ("Offers to recover your money are a second scam", "If you have lost money, anyone who contacts you offering to recover it for a fee is another fraudster. Real help never asks for money up front."),
        ),
        "marketplaces": _t(
            "Buying and selling between individuals is full of fake buyers, fake sellers and fake proof.",
            ("Keep payment inside the platform", "Use the platform's own payment protection. Refuse offers to move to WhatsApp, a courier or a 'secure payment link' sent by the other person."),
            ("Receiving money never needs your approval", "A buyer who asks you to scan a code, click a link, enter your PIN or approve a payment in order to 'receive' money is taking money from you."),
            ("Do not trust screenshots", "Proof of payment, emails and 'bank' messages can all be forged. Check your own account in your banking app."),
            ("Meet and inspect when you can", "For valuable items, meet in person, inspect the item, and pay only when you have it. A price that is far too good, or a seller who cannot meet or video call, is a warning."),
            ("Watch for overpayment", "A buyer who sends too much and asks you to return the difference is a standard scam. The first payment will be reversed or never arrive."),
        ),
        "your_accounts": _t(
            "You cannot prevent every attempt, so limit what any single mistake can cost.",
            ("Set limits", "Lower the daily and per-transfer limits in your banking app, and raise them only when you need to."),
            ("Turn notifications on", "Enable payment notifications on your phone, so you see every movement straight away."),
            ("Separate your savings", "Keep savings in an account you do not use and do not see in your everyday app, so a scammer who reaches your app cannot empty it in one go."),
            ("Never share codes or remote access", "No one needs your codes, your itsme approval or access to your screen: not the bank, not support, not the police. If remote access was given, disconnect and change your passwords from another device."),
            ("Strong, separate logins", "Use a different password for every account and a password manager, and turn on the strongest second step available, such as passkeys or a hardware key."),
            ("Install only from official stores", "Be wary of apps and 'security updates' that come through a link or ask you to change settings on your phone. Keep your devices updated."),
            ("Check regularly", "Review your devices, your approved payees and your recent payments from time to time."),
        ),
    },
    "fr": {
        "zero_trust": _t(
            "La fraude moderne ne ressemble pas à une fraude. Ses auteurs sont des professionnels qui testent ce qui marche, donc les anciens signaux d'alerte ne sont plus fiables. Considérez tout contact inattendu comme non vérifié, même s'il paraît tout à fait réel, et vérifiez-le vous-même par un canal que vous maîtrisez.",
            ("Il n'existe pas de signe fiable", "Les fautes, la précipitation, les menaces et les accents bizarres relèvent des arnaques bon marché. Les fraudeurs habiles sont polis, patients et bien préparés. Certains ne montrent volontairement aucune urgence, car une personne calme qui dit « prenez votre temps » inspire confiance. Certains vont même jusqu'à dire « raccrochez et appelez votre banque », puis contrôlent la suite. Jugez ce qu'on vous demande, jamais la manière dont on vous le demande."),
            ("Savoir des choses sur vous ne prouve rien", "Votre nom, votre adresse, votre banque, vos derniers paiements et vos proches peuvent provenir de fuites de données, d'anciennes arnaques, de registres publics et des réseaux sociaux. Un appelant ou un message qui les connaît n'est pas plus susceptible d'être authentique."),
            ("Vérifiez par un canal que vous choisissez", "N'utilisez jamais un numéro, un lien, une adresse ou un nom donné par l'autre personne pour la vérifier. Cherchez vous-même le vrai numéro au dos de votre carte ou sur un courrier officiel, tapez vous-même l'adresse web ou ouvrez vous-même l'application. Un vrai numéro affiché ne prouve rien non plus : les numéros et les noms d'expéditeur peuvent être falsifiés."),
            ("Une voix ou un visage n'est pas une preuve", "À partir de quelques secondes d'enregistrement, l'IA peut copier la voix de votre mère, de votre père ou de votre enfant, et la vidéo en direct peut aussi être truquée. Une voix familière au téléphone, même en pleurs ou en détresse, ne prouve plus que c'est bien la personne. Convenez en personne d'un mot de passe familial, et lisez le sujet sur la famille, les voix et la vidéo."),
            ("Regardez ce qu'on demande, pas qui le demande", "Arrêtez-vous dès que quelqu'un vous demande d'envoyer de l'argent, de le déplacer vers un compte « sûr », de lire ou d'approuver un code, d'installer une application, de partager votre écran ou de modifier un plafond. Une vraie banque, un vrai policier ou une vraie entreprise n'a besoin d'aucune de ces choses. Quelle que soit la voix, le logo ou l'histoire, la réponse est non."),
            ("Si vous n'êtes pas sûr à 100 %, ne faites rien de risqué", "Pas de virement, pas de code, pas d'application, pas de nouveau bénéficiaire tant que vous n'avez pas vérifié. Attendre un jour ne vous coûte rien : un vrai problème sera toujours là. L'absence de pression ne signifie pas que tout est sûr : ne montrer aucune urgence est aussi une technique."),
            ("Allez sur place", "Il n'y a aucun mal à entrer dans votre agence bancaire avec votre téléphone ou votre ordinateur pour demander si quelque chose est réel. Personne ne vous prendra pour un naïf ; le personnel est content quand les clients vérifient. Trouvez vous-même l'adresse sur votre carte, votre extrait ou le site officiel de la banque, et demandez qu'on regarde votre compte et qu'on vous montre ce qui est sûr."),
            ("Parlez d'abord à quelqu'un de confiance", "Avant tout paiement important ou inhabituel, parlez-en à une personne de confiance et écoutez ses doutes. Les fraudeurs demandent souvent le secret (« la banque est impliquée », « n'en parlez pas au personnel »). Toute consigne de cacher quelque chose aux personnes qui tiennent à vous est une raison de leur en parler."),
            ("Limitez les dégâts", "Baissez votre plafond de virement dans votre application bancaire, activez les notifications de paiement, gardez votre épargne sur un compte séparé absent de votre application quotidienne, et utilisez un délai ou une double approbation pour les nouveaux bénéficiaires si votre banque le propose."),
            ("Se faire avoir n'est pas être idiot", "Ces opérations sont gérées comme des entreprises, avec des scripts, des recherches et des équipes. Des personnes prudentes et intelligentes se font piéger chaque jour. Si cela vous arrive, agissez vite et parlez-en : cela vous protège, vous et les autres."),
        ),
        "phone_calls": _t(
            "La fraude par téléphone a dépassé l'appelant maladroit. Les appelants d'aujourd'hui peuvent paraître calmes, serviables et parfaitement informés. Appliquez les règles ci-dessous même quand tout semble normal.",
            ("Le numéro affiché peut être falsifié", "Un appel peut afficher le vrai numéro de votre banque, ou apparaître dans la même liste que de précédents appels authentiques. L'affichage ne prouve rien. Il en va de même pour un message vocal ou un SMS reçu juste après l'appel."),
            ("Un appelant calme n'est pas un appelant sûr", "Certains fraudeurs vous mettent la pression. Les meilleurs sont patients, chaleureux et ne sont pas pressés. Ils peuvent même dire que vous pouvez raccrocher et appeler la banque vous-même, pour que vous vous sentiez maître de la situation. Ensuite, ils orientent la suite : un numéro qu'ils vous ont donné, un second « collègue » qui répond, ou un appel qui ne s'est jamais vraiment terminé. Décidez seul, avec vos propres démarches."),
            ("Comment vérifier correctement", "Terminez l'appel. Attendez quelques minutes, ou utilisez un autre téléphone si possible. Cherchez ensuite vous-même le numéro, au dos de votre carte ou sur le site officiel de la banque que vous avez tapé, et demandez si l'appel était réel. Mieux encore, rendez-vous en agence."),
            ("Ce qu'une vraie banque ne demande jamais", "Déplacer de l'argent pour le protéger, approuver ou annuler un paiement dans l'application sur leur instruction, installer une application, partager votre écran, lire des codes ou des approbations itsme, ou donner des données de carte. Si l'une de ces choses est demandée, c'est une fraude, quelle que soit la force de conviction de la personne."),
            ("Ne dites pas oui et n'appuyez sur rien", "De courtes réponses comme « oui » peuvent être enregistrées et réutilisées. Si un appel vous semble louche, ne dites rien de plus et raccrochez."),
            ("Les offres d'aide sont suspectes", "Les appels du « support technique », de « la police », de « l'administration fiscale » ou d'une « équipe antifraude » que vous n'avez pas sollicités sont la porte d'entrée. Les vraies organisations vous écrivent ou vous laissent les contacter."),
            ("Parlez-en à quelqu'un", "Dites à voix haute ce qu'on vous demande, à une personne de confiance. Les escrocs comptent sur le fait que vous êtes seul face à l'appel."),
        ),
        "messages_and_links": _t(
            "Le phishing est aujourd'hui bien rédigé, bien présenté et souvent impossible à distinguer du réel. Ne comptez pas sur votre capacité à le repérer : changez votre façon d'agir.",
            ("Ne vous connectez jamais via un lien", "Quoi que dise le message, ouvrez l'application de votre banque ou tapez vous-même son adresse web. Les faux sites copient parfaitement logos, textes et même chat en direct. Une seule lettre changée dans l'adresse est souvent la seule différence."),
            ("Le même fil de discussion ne prouve rien", "Des SMS frauduleux peuvent apparaître dans la même conversation que les vrais messages de votre banque, et de faux e-mails peuvent afficher le bon nom d'expéditeur. Un message qui apparaît au bon endroit n'est pas une preuve."),
            ("Un langage parfait est devenu normal", "L'IA écrit un néerlandais, un français et un anglais sans faute. L'absence de fautes ne vous apprend rien."),
            ("Lisez ce que vous approuvez", "Une demande itsme ou dans l'application bancaire que vous n'avez pas lancée vous-même est un signal d'alerte. Lisez le montant, le bénéficiaire et l'action à l'écran avant de confirmer. N'approuvez pas une demande simplement parce qu'elle paraît banale."),
            ("Les codes QR et les pièces jointes sont aussi des liens", "Un code QR, un PDF, une demande de paiement ou un avis de « livraison » peut mener aux mêmes fausses pages. Idem pour les messages indiquant que vous avez reçu un remboursement ou envoyé un paiement par erreur."),
            ("Signalez-les", "Transférez les messages suspects à verdacht@safeonweb.be, puis supprimez-les. Ne répondez pas, même pour dire stop."),
        ),
        "family_voices": _t(
            "Un appel ou une vidéo d'un proche peut désormais être faux. Quelques secondes de sa voix, tirées d'une vidéo sur les réseaux sociaux ou d'un message vocal, suffisent pour la copier, avec le ton, l'accent et la façon de parler. Préparez-vous avant que cela n'arrive.",
            ("Les voix peuvent être clonées", "Des escrocs peuvent imiter votre enfant, votre partenaire, votre parent ou votre petit-enfant et dire qu'il est en difficulté : accident, arrestation, téléphone perdu, nouveau numéro. Cela peut sonner exactement comme lui, même en pleurs. Une voix familière n'est plus une preuve."),
            ("La vidéo n'est pas non plus une preuve", "La vidéo en direct peut aussi être truquée ou modifiée. Un appel vidéo montrant un visage connu vaut mieux qu'une voix, mais n'est toujours pas certain, surtout quand on vous demande quelque chose d'étrange ou d'urgent."),
            ("Convenez d'un mot de passe, en personne", "Choisissez ensemble, face à face, un mot ou une question que personne ne pourrait trouver en ligne : pas le nom d'un animal ni un lieu de naissance. Ne l'écrivez ni ne le dites jamais dans des messages. Changez-le après usage. Demandez-le dès qu'il est question d'argent ou de secrets."),
            ("Brisez le cercle", "Raccrochez. Rappelez la personne au numéro que vous avez déjà, ou appelez quelqu'un qui est avec elle. Si vous ne pouvez pas la joindre, demandez à un proche, rendez-vous sur place ou attendez. Une vraie urgence survit à quelques minutes de vérification."),
            ("Méfiez-vous de toute demande d'argent", "Virements vers un nouveau compte, cartes cadeaux, cryptomonnaie, espèces remises à un coursier, ou nouveau numéro « parce que le mien est cassé » : ce sont des classiques. Tout comme la demande de garder le secret."),
            ("Aidez vos parents et grands-parents", "Parlez-en calmement, sans faire la leçon. Convenez qu'ils vous appellent toujours avant tout paiement inhabituel, aussi convaincant que soit l'appelant, et que raccrocher est toujours permis. Aidez-les à baisser leur plafond de virement et à activer les alertes de paiement, et prenez régulièrement de leurs nouvelles."),
            ("Limitez ce qui est public", "Plus votre voix et les détails de votre famille sont publics, plus il est facile de les copier. Gardez vos réseaux sociaux privés autant que possible et évitez de publier ouvertement des extraits de voix d'enfants et de proches âgés."),
        ),
        "investments": _t(
            "La fraude à l'investissement est lente et patiente. Ses auteurs consacrent souvent des semaines d'attention à votre personne avant de demander beaucoup.",
            ("La confiance se construit dans le temps", "Cela peut commencer par une amitié ou une histoire d'amour sur une messagerie, ou par un « conseiller » serviable. Ils montrent des gains impressionnants mais plausibles, partagent des captures d'écran et vous laissent parfois retirer une petite somme. Un premier paiement ne prouve rien : c'est un appât."),
            ("Vérifiez vous-même la société", "Cherchez la société dans le registre de la FSMA et sa liste d'avertissements (fsma.be). Les escrocs copient les noms, numéros d'agrément et sites de vraies sociétés : vérifiez donc que le site, l'adresse et le numéro de téléphone correspondent au registre officiel, que vous avez trouvé vous-même."),
            ("Méfiez-vous des garanties et des « tuyaux »", "Personne ne peut garantir des rendements. Des rendements modestes peuvent être un mensonge tout comme des rendements énormes. Quiconque vous oriente vers une plateforme que vous ne pouvez pas visiter ou vers des transferts en cryptomonnaie que vous ne comprenez pas mérite une méfiance accrue."),
            ("Ralentissez et demandez", "Parlez-en à une personne de confiance, demandez l'avis d'un conseiller indépendant et interrogez votre banque en agence. Si votre banque vous met en garde contre un paiement, prenez l'avertissement au sérieux, même si l'autre personne vous a dit que la banque se trompe."),
            ("Les offres de récupération sont une deuxième arnaque", "Si vous avez perdu de l'argent, quiconque vous contacte pour le récupérer contre rémunération est un autre fraudeur. Une vraie aide ne demande jamais d'argent à l'avance."),
        ),
        "marketplaces": _t(
            "L'achat et la vente entre particuliers regorgent de faux acheteurs, de faux vendeurs et de fausses preuves.",
            ("Gardez le paiement dans la plateforme", "Utilisez la protection de paiement de la plateforme. Refusez de passer à WhatsApp, à un coursier ou à un « lien de paiement sécurisé » envoyé par l'autre personne."),
            ("Recevoir de l'argent ne demande jamais votre approbation", "Un acheteur qui vous demande de scanner un code, de cliquer sur un lien, de saisir votre code PIN ou d'approuver un paiement pour « recevoir » de l'argent vous en prend."),
            ("Ne vous fiez pas aux captures d'écran", "Les preuves de paiement, les e-mails et les messages de « banque » peuvent tous être falsifiés. Vérifiez votre propre compte dans votre application bancaire."),
            ("Rencontrez et inspectez si possible", "Pour les objets de valeur, rencontrez la personne, inspectez l'objet et ne payez que lorsque vous l'avez. Un prix bien trop beau, ou un vendeur qui ne peut ni vous rencontrer ni faire un appel vidéo, est un signal d'alerte."),
            ("Attention au trop-perçu", "Un acheteur qui envoie trop et vous demande de rembourser la différence est une arnaque classique. Le premier paiement sera annulé ou n'arrivera jamais."),
        ),
        "your_accounts": _t(
            "Vous ne pouvez pas empêcher chaque tentative, alors limitez ce qu'une seule erreur peut coûter.",
            ("Fixez des plafonds", "Baissez les plafonds journalier et par virement dans votre application bancaire, et ne les relevez que lorsque vous en avez besoin."),
            ("Activez les notifications", "Activez les notifications de paiement sur votre téléphone pour voir chaque mouvement immédiatement."),
            ("Séparez votre épargne", "Gardez votre épargne sur un compte que vous n'utilisez pas et que vous ne voyez pas dans votre application quotidienne, pour qu'un escroc qui accède à votre application ne puisse pas le vider d'un coup."),
            ("Ne partagez jamais de codes ni d'accès à distance", "Personne n'a besoin de vos codes, de votre approbation itsme ni d'un accès à votre écran : ni la banque, ni le support, ni la police. Si un accès à distance a été donné, déconnectez-vous et changez vos mots de passe depuis un autre appareil."),
            ("Des identifiants forts et distincts", "Utilisez un mot de passe différent pour chaque compte et un gestionnaire de mots de passe, et activez la seconde étape la plus forte disponible, comme les clés d'accès (passkeys) ou une clé physique."),
            ("N'installez que depuis les magasins officiels", "Méfiez-vous des applications et des « mises à jour de sécurité » reçues par un lien ou qui vous demandent de modifier des réglages de votre téléphone. Gardez vos appareils à jour."),
            ("Vérifiez régulièrement", "Passez en revue de temps en temps vos appareils, vos bénéficiaires approuvés et vos paiements récents."),
        ),
    },
    "nl": {
        "zero_trust": _t(
            "Moderne fraude ziet er niet uit als fraude. De daders zijn professionals die testen wat werkt, dus de oude waarschuwingssignalen zijn niet meer betrouwbaar. Beschouw elk onverwacht contact als niet gecontroleerd, hoe echt het ook aanvoelt, en controleer het zelf via een kanaal dat jij beheerst.",
            ("Er bestaan geen betrouwbare kenmerken", "Typefouten, haast, dreigementen en vreemde accenten horen bij de goedkope oplichting. De bekwame oplichters zijn beleefd, geduldig en goed voorbereid. Sommigen tonen met opzet helemaal geen haast, want iemand die rustig zegt 'neem je tijd' wekt vertrouwen. Sommigen zeggen zelfs 'hang op en bel je bank' en sturen daarna wat volgt. Beoordeel wat er gevraagd wordt, nooit hoe het gevraagd wordt."),
            ("Dingen over jou weten bewijst niets", "Je naam, adres, bank, recente betalingen en familieleden kunnen afkomstig zijn van datalekken, eerdere oplichtingen, openbare registers en sociale media. Een beller of bericht dat ze kent, is daarom niet waarschijnlijker echt."),
            ("Controleer via een kanaal dat je zelf kiest", "Gebruik nooit een nummer, link, adres of naam dat de andere persoon je gaf om hem of haar te controleren. Zoek zelf het echte nummer op de achterkant van je kaart of in een officiële brief, typ zelf het webadres of open zelf de app. Een echt nummer op je scherm bewijst ook niets: nummers en afzendernamen kunnen vervalst worden."),
            ("Een stem of gezicht is geen bewijs", "Met een paar seconden opgenomen spraak kan AI de stem van je moeder, vader of kind nabootsen, en ook live video kan vervalst worden. Een bekende stem aan de telefoon, zelfs huilend of in nood, bewijst niet meer dat zij het zijn. Spreek persoonlijk een codewoord af en lees het onderwerp over familie, stemmen en video."),
            ("Kijk naar wat er gevraagd wordt, niet naar wie het vraagt", "Stop zodra iemand je vraagt geld te sturen, het naar een 'veilige' rekening over te zetten, een code door te geven of goed te keuren, een app te installeren, je scherm te delen of een limiet te wijzigen. Een echte bank, politieagent of onderneming heeft dat nooit nodig. Welke stem, welk logo of welk verhaal ook, het antwoord is nee."),
            ("Als je niet 100% zeker bent, doe niets riskants", "Geen overschrijving, geen code, geen app, geen nieuwe begunstigde zolang je niet hebt gecontroleerd. Een dag wachten kost je niets: een echt probleem is er nog steeds. Geen druk betekent niet dat het veilig is: geen haast tonen is ook een techniek."),
            ("Ga langs", "Er is niets mis mee om met je telefoon of laptop naar je bankkantoor te stappen en te vragen of iets echt is. Niemand zal je dwaas vinden; het personeel is blij als klanten controleren. Zoek het adres zelf op via je kaart, je rekeninguittreksel of de officiële website van de bank, en vraag om naar je rekening te kijken en je te tonen wat veilig is."),
            ("Praat eerst met iemand die je vertrouwt", "Vertel vóór elke grote of ongewone betaling aan iemand die je vertrouwt wat er aan de hand is en luister naar zijn of haar twijfels. Oplichters vragen vaak om geheimhouding ('de bank is erbij betrokken', 'zeg het niet tegen het personeel'). Elke opdracht om iets te verbergen voor mensen die om je geven, is een reden om het hun net te vertellen."),
            ("Beperk de schade", "Verlaag je overschrijvingslimiet in je bankapp, schakel betalingsmeldingen in, houd je spaargeld op een aparte rekening die niet in je dagelijkse app staat en gebruik een vertraging of tweede goedkeuring voor nieuwe begunstigden als je bank dat aanbiedt."),
            ("Voor de gek gehouden worden is niet dom zijn", "Deze operaties worden als bedrijven gerund, met scripts, onderzoek en teams. Voorzichtige, intelligente mensen worden elke dag opgelicht. Als het jou overkomt, handel dan snel en praat erover: het beschermt jou en anderen."),
        ),
        "phone_calls": _t(
            "Telefoonfraude is verder gegaan dan de onhandige beller. De bellers van vandaag kunnen rustig, behulpzaam en perfect geïnformeerd overkomen. Pas de regels hieronder toe, ook als alles juist lijkt.",
            ("Het getoonde nummer kan vervalst zijn", "Een oproep kan het echte nummer van je bank tonen of in dezelfde lijst verschijnen als eerdere echte oproepen. Wat het scherm toont bewijst niets. Hetzelfde geldt voor een voicemail of sms die vlak na het gesprek binnenkomt."),
            ("Een rustige beller is geen veilige beller", "Sommige oplichters zetten je onder druk. De betere zijn geduldig, warm en hebben geen haast. Ze kunnen zelfs zeggen dat je mag ophangen en zelf je bank bellen, zodat je je in controle voelt. Daarna sturen ze wat volgt: een nummer dat ze je gaven, een tweede 'collega' die opneemt, of een gesprek dat nooit echt beëindigd werd. Beslis zelf, met je eigen stappen."),
            ("Hoe je goed controleert", "Beëindig het gesprek. Wacht een paar minuten of gebruik indien mogelijk een andere telefoon. Zoek dan zelf het nummer op, op de achterkant van je kaart of op de officiële website van de bank die je zelf intikte, en vraag of het gesprek echt was. Nog beter: ga naar een kantoor."),
            ("Wat een echte bank nooit vraagt", "Geld verplaatsen om het te beschermen, een betaling in de app goedkeuren of annuleren op hun aanwijzing, een app installeren, je scherm delen, codes of itsme-goedkeuringen doorgeven of kaartgegevens geven. Wordt een van die dingen gevraagd, dan is het fraude, hoe overtuigend de persoon ook is."),
            ("Zeg geen ja en druk nergens op", "Korte antwoorden zoals 'ja' kunnen worden opgenomen en hergebruikt. Als een gesprek niet klopt, zeg dan niets meer en hang op."),
            ("Hulpaanbiedingen zijn verdacht", "Oproepen van 'technische ondersteuning', 'de politie', 'de belastingdienst' of een 'fraudeteam' waar je niet om vroeg, zijn de manier om binnen te raken. Echte organisaties schrijven je of laten je zelf contact opnemen."),
            ("Praat erover", "Zeg hardop wat er gevraagd wordt, tegen iemand die je vertrouwt. Oplichters rekenen erop dat je alleen met het gesprek zit."),
        ),
        "messages_and_links": _t(
            "Phishing is tegenwoordig goed geschreven, goed vormgegeven en vaak niet van echt te onderscheiden. Reken niet op het herkennen ervan: verander hoe je handelt.",
            ("Log nooit in via een link", "Wat het bericht ook zegt, open de app van je bank of typ zelf het webadres. Nepsites kopiëren logo's, teksten en zelfs de livechat perfect. Eén veranderde letter in het adres is vaak het enige verschil."),
            ("Dezelfde conversatie bewijst niets", "Frauduleuze sms'en kunnen in dezelfde conversatie verschijnen als de echte berichten van je bank en valse e-mails kunnen de juiste afzendernaam tonen. Een bericht op de juiste plaats is geen bewijs."),
            ("Perfecte taal is nu normaal", "AI schrijft vlekkeloos Nederlands, Frans en Engels. Het ontbreken van fouten zegt je niets."),
            ("Lees wat je goedkeurt", "Een itsme- of bankappverzoek dat je zelf niet startte, is een waarschuwing. Lees het bedrag, de begunstigde en de actie op het scherm voor je bevestigt. Keur een verzoek niet goed omdat het routine lijkt."),
            ("QR-codes en bijlagen zijn ook links", "Een QR-code, een pdf, een betaalverzoek of een 'leveringsbericht' kan naar dezelfde valse pagina's leiden. Hetzelfde geldt voor berichten dat je een terugbetaling kreeg of per vergissing een betaling deed."),
            ("Meld ze", "Stuur verdachte berichten door naar verdacht@safeonweb.be en verwijder ze. Antwoord niet, ook niet om te zeggen dat ze moeten stoppen."),
        ),
        "family_voices": _t(
            "Een oproep of video van iemand van wie je houdt, kan nu nep zijn. Een paar seconden van hun stem uit een video op sociale media of een voicemail volstaan om ze te kopiëren, met toon, accent en manier van praten. Bereid je voor voor het gebeurt.",
            ("Stemmen kunnen gekloond worden", "Oplichters kunnen je kind, partner, ouder of kleinkind nabootsen en zeggen dat die in de problemen zit: een ongeval, een arrestatie, een verloren telefoon, een nieuw nummer. Het kan precies als die persoon klinken, zelfs huilend. Een bekende stem is geen bewijs meer."),
            ("Video is ook geen bewijs", "Live video kan ook vervalst of aangepast worden. Een videogesprek met een bekend gezicht is beter dan een stem, maar nog niet zeker, zeker als er iets vreemds of dringends gevraagd wordt."),
            ("Spreek persoonlijk een codewoord af", "Kies samen, van aangezicht tot aangezicht, een woord of een vraag die niemand online kan vinden: niet de naam van een huisdier of een geboorteplaats. Schrijf of zeg het nooit in berichten. Verander het na gebruik. Vraag ernaar zodra er geld of geheimen in het spel zijn."),
            ("Doorbreek de lus", "Hang op. Bel de persoon terug op het nummer dat je al hebt, of bel iemand die bij die persoon is. Als je hem of haar niet bereikt, vraag het aan een familielid, ga langs of wacht. Een echt noodgeval overleeft een paar minuten controle."),
            ("Wees op je hoede voor elke vraag om geld", "Overschrijvingen naar een nieuwe rekening, cadeaukaarten, crypto, cash aan een koerier of een nieuw nummer 'omdat de mijne kapot is' zijn klassiekers. Net als de vraag om het geheim te houden."),
            ("Help ouders en grootouders", "Praat er rustig over, zonder les te geven. Spreek af dat ze altijd eerst jou bellen vóór een ongewone betaling, hoe overtuigend de beller ook is, en dat ophangen altijd mag. Help hen hun overschrijvingslimiet te verlagen en betalingsmeldingen in te schakelen, en neem regelmatig contact op."),
            ("Beperk wat openbaar is", "Hoe meer van je stem en de gegevens van je familie openbaar zijn, hoe makkelijker ze te kopiëren zijn. Houd je sociale media waar mogelijk privé en vermijd het openlijk posten van stemfragmenten van kinderen en oudere familieleden."),
        ),
        "investments": _t(
            "Beleggingsfraude is traag en geduldig. De daders besteden vaak weken aandacht aan jou voor ze veel vragen.",
            ("Vertrouwen wordt in de tijd opgebouwd", "Het kan beginnen als vriendschap of romance op een berichtendienst, of als een behulpzame 'adviseur'. Ze tonen indrukwekkende maar aannemelijke winsten, delen screenshots en laten je soms een klein bedrag opnemen. Een eerste uitbetaling bewijst niets: het is lokaas."),
            ("Controleer het bedrijf zelf", "Zoek het bedrijf op in het register van de FSMA en op de waarschuwingslijst (fsma.be). Oplichters kopiëren namen, vergunningsnummers en websites van echte bedrijven, dus controleer of de website, het adres en het telefoonnummer overeenkomen met het officiële register, dat je zelf opzocht."),
            ("Wees op je hoede voor garanties en 'tips van binnenuit'", "Niemand kan rendement garanderen. Bescheiden rendementen kunnen net zo goed een leugen zijn als enorme. Wie je naar een platform stuurt dat je niet kunt bezoeken, of naar cryptotransfers die je niet begrijpt, verdient extra wantrouwen."),
            ("Vertraag en vraag raad", "Praat met iemand die je vertrouwt, vraag een onafhankelijke adviseur en vraag het je bank persoonlijk. Als je bank je voor een betaling waarschuwt, neem die waarschuwing dan serieus, ook al zei de andere persoon dat de bank zich vergist."),
            ("Aanbiedingen om je geld terug te halen zijn een tweede oplichting", "Als je geld hebt verloren, is iedereen die contact opneemt om het tegen betaling terug te halen een andere oplichter. Echte hulp vraagt nooit vooraf geld."),
        ),
        "marketplaces": _t(
            "Kopen en verkopen tussen particulieren zit vol valse kopers, valse verkopers en vals bewijs.",
            ("Houd de betaling binnen het platform", "Gebruik de betalingsbescherming van het platform. Weiger over te stappen naar WhatsApp, een koerier of een 'veilige betaallink' die de andere persoon stuurt."),
            ("Geld ontvangen vraagt nooit je goedkeuring", "Een koper die vraagt een code te scannen, op een link te klikken, je pincode in te voeren of een betaling goed te keuren om geld te 'ontvangen', neemt geld van je af."),
            ("Vertrouw screenshots niet", "Betaalbewijzen, e-mails en 'bank'-berichten kunnen allemaal vervalst zijn. Controleer je eigen rekening in je bankapp."),
            ("Spreek af en inspecteer als je kunt", "Spreek voor waardevolle voorwerpen persoonlijk af, bekijk het voorwerp en betaal pas als je het hebt. Een veel te mooie prijs, of een verkoper die niet kan afspreken of videobellen, is een waarschuwing."),
            ("Let op overbetaling", "Een koper die te veel overmaakt en vraagt het verschil terug te storten, is een standaardoplichting. De eerste betaling wordt teruggedraaid of komt nooit aan."),
        ),
        "your_accounts": _t(
            "Je kunt niet elke poging voorkomen, dus beperk wat één vergissing kan kosten.",
            ("Stel limieten in", "Verlaag de dag- en overschrijvingslimieten in je bankapp en verhoog ze alleen als je het nodig hebt."),
            ("Zet meldingen aan", "Schakel betalingsmeldingen in op je telefoon, zodat je elke beweging meteen ziet."),
            ("Scheid je spaargeld", "Houd je spaargeld op een rekening die je niet gebruikt en niet in je dagelijkse app ziet, zodat een oplichter die in je app geraakt, ze niet in één keer kan leegmaken."),
            ("Deel nooit codes of toegang op afstand", "Niemand heeft je codes, je itsme-goedkeuring of toegang tot je scherm nodig: niet de bank, niet de helpdesk, niet de politie. Als je toegang op afstand hebt gegeven, koppel dan los en wijzig je wachtwoorden vanaf een ander toestel."),
            ("Sterke, aparte logins", "Gebruik voor elke account een ander wachtwoord en een wachtwoordbeheerder, en schakel de sterkste tweede stap in die beschikbaar is, zoals passkeys of een hardwaresleutel."),
            ("Installeer alleen via officiële winkels", "Wees op je hoede voor apps en 'beveiligingsupdates' die je via een link krijgt of die vragen instellingen op je telefoon te wijzigen. Houd je toestellen up-to-date."),
            ("Controleer regelmatig", "Overloop af en toe je toestellen, je goedgekeurde begunstigden en je recente betalingen."),
        ),
    },
}

TERMS = {
    "en": {
        "draft_notice": "Draft terms for the pilot. They have not been reviewed by a lawyer yet.",
        "fee": [
            "20% plus VAT of the money you recover thanks to Fraud Aid.",
            "A further 10% plus VAT only if your case has to go to Ombudsfin or to legal action.",
            "Nothing if nothing is recovered.",
            "We never charge for money your bank had already refunded to you before we sent your claim.",
        ],
        "we_do": [
            "Send your claim to your bank and ask them to recall the payment from the receiving bank.",
            "Follow up, answer the bank's questions and keep you updated.",
            "Escalate to Ombudsfin if the bank refuses. If your case needs a lawyer, we agree it with you first.",
        ],
        "you_do": [
            "Give us true and complete information and the documents we ask for.",
            "Tell us at once if your bank contacts you or refunds you directly.",
        ],
        "rights": [
            "You can withdraw before we send your claim and pay nothing.",
            "You can delete your case and all your files at any time from your case page.",
        ],
        "privacy": "We store your answers, details and files to handle your claim. Only Fraud Aid staff and a partner lawyer working on your case can see them.",
        "mandate": (
            "I authorise Fraud Aid to act on my behalf to claim a refund for the fraud I described: to contact and negotiate with my bank, "
            "the receiving bank and Ombudsfin, and to send and receive correspondence about it. I remain the owner of my claim."
        ),
        "share": "Optional: share the scammer's identifiers (IBAN, phone number, website) and the scam pattern, without my name, with banks and the police to help stop this fraud.",
    },
    "fr": {
        "draft_notice": "Conditions provisoires pour le projet pilote. Elles n'ont pas encore été revues par un avocat.",
        "fee": [
            "20 % de l'argent que vous récupérez grâce à Fraud Aid, plus la TVA.",
            "10 % supplémentaires, plus la TVA, seulement si votre dossier doit aller devant Ombudsfin ou en action en justice.",
            "Rien si rien n'est récupéré.",
            "Nous ne facturons jamais l'argent que votre banque vous avait déjà remboursé avant l'envoi de votre réclamation.",
        ],
        "we_do": [
            "Envoyer votre réclamation à votre banque et lui demander de rappeler le paiement auprès de la banque destinataire.",
            "Faire le suivi, répondre aux questions de la banque et vous tenir informé.",
            "Escalader vers Ombudsfin si la banque refuse. Si votre dossier nécessite un avocat, nous en convenons d'abord avec vous.",
        ],
        "you_do": [
            "Nous donner des informations vraies et complètes ainsi que les documents demandés.",
            "Nous prévenir immédiatement si votre banque vous contacte ou vous rembourse directement.",
        ],
        "rights": [
            "Vous pouvez vous rétracter avant l'envoi de votre réclamation sans rien payer.",
            "Vous pouvez supprimer votre dossier et tous vos fichiers à tout moment depuis la page de votre dossier.",
        ],
        "privacy": "Nous conservons vos réponses, vos coordonnées et vos fichiers pour traiter votre réclamation. Seuls le personnel de Fraud Aid et un avocat partenaire qui travaille sur votre dossier peuvent les consulter.",
        "mandate": (
            "J'autorise Fraud Aid à agir en mon nom pour réclamer le remboursement de la fraude que j'ai décrite : contacter et négocier avec ma banque, "
            "la banque destinataire et Ombudsfin, et envoyer et recevoir la correspondance s'y rapportant. Je reste propriétaire de ma créance."
        ),
        "share": "Facultatif : partager les identifiants de l'escroc (IBAN, numéro de téléphone, site web) et le schéma de l'arnaque, sans mon nom, avec les banques et la police pour aider à arrêter cette fraude.",
    },
    "nl": {
        "draft_notice": "Voorlopige voorwaarden voor de pilot. Ze zijn nog niet door een advocaat nagekeken.",
        "fee": [
            "20% van het geld dat je dankzij Fraud Aid terugkrijgt, plus btw.",
            "Nog eens 10%, plus btw, alleen als je dossier naar Ombudsfin of voor de rechter moet.",
            "Niets als er niets wordt teruggekregen.",
            "We rekenen nooit kosten aan voor geld dat je bank je al had terugbetaald voordat we je claim verstuurden.",
        ],
        "we_do": [
            "Je claim naar je bank sturen en haar vragen de betaling terug te halen bij de ontvangende bank.",
            "Opvolgen, de vragen van de bank beantwoorden en je op de hoogte houden.",
            "Doorverwijzen naar Ombudsfin als de bank weigert. Als je dossier een advocaat nodig heeft, spreken we dat eerst met jou af.",
        ],
        "you_do": [
            "Ons juiste en volledige informatie geven en de gevraagde documenten.",
            "Ons meteen verwittigen als je bank contact met je opneemt of je rechtstreeks terugbetaalt.",
        ],
        "rights": [
            "Je kunt je terugtrekken voor we je claim versturen zonder iets te betalen.",
            "Je kunt je dossier en al je bestanden op elk moment verwijderen via je dossierpagina.",
        ],
        "privacy": "We bewaren je antwoorden, gegevens en bestanden om je claim te behandelen. Alleen medewerkers van Fraud Aid en een partneradvocaat die aan je dossier werkt kunnen ze zien.",
        "mandate": (
            "Ik machtig Fraud Aid om namens mij een terugbetaling te vragen voor de fraude die ik heb beschreven: contact opnemen en onderhandelen met mijn bank, "
            "de ontvangende bank en Ombudsfin, en de briefwisseling daarover versturen en ontvangen. Ik blijf eigenaar van mijn vordering."
        ),
        "share": "Optioneel: de gegevens van de oplichter (IBAN, telefoonnummer, website) en het patroon van de oplichting, zonder mijn naam, delen met banken en de politie om deze fraude te helpen stoppen.",
    },
}
