# Fraud Aid

Free first aid for scam victims in Belgium. A victim describes what happened, a local LLM extracts the facts, fixed rules say where they stand under Belgian and EU payment law, and they get a non-binding estimate plus the next steps. Victims who want help can join a waitlist (success-fee model, planned).

## How it works

The site is a guided flow with Suki, one question per screen: scammed or learn more, country, amount, how it happened (options plus your own words), who they pretended to be, whether you approved the payment, how you paid, when, your bank, and a few last checks (shared codes, remote access, already told the bank or police, scammer details, document language). If Fraud Aid can take the case on (`POST /api/verdict`, no AI call), people then choose between doing it themselves (free) and letting Fraud Aid help, with an "i" that explains the percentage. Other cases go straight to their own plan. The do-it-yourself plan ends with a "Still need help?" box. The plan is a fixed order: call Card Stop, report to the police, call the bank and send a written claim, claim the money back, protect yourself.

Everything the user relies on is deterministic:
- `app/assess.py`: the verdict (strong, possible, unlikely, unclear) from plain rules.
- `app/plan.py`: builds the five steps from the answers. Only the wording of the steps changes with the answers.
- `app/tools.py`: claim letter and police report templates in Dutch, French and English, plus protection tips.

The only LLM call is `summarize` in `app/plan.py`: the local model (`ministral-3:8b` through Ollama) rewrites the user's own words into a short first-person statement for the two documents. If it fails the user's own words are used. The statement is shown for the user to check.

Why no free chat or tool calling: in testing the 8B model skipped the tool, claimed to have "checked with KBC", invented a bank phone number and email, and wrote a letter citing Dutch law. Do not go back to free generation for anything legal without a much stronger model and an evaluation set. The summary also needs watching: it once added a made-up denial, and wrote "telefoonoproef" for "telefoonoproep".

- `app/main.py`: FastAPI. Free flow: `POST /api/plan`, `GET /api/tips`, `POST /api/waitlist` (explicit consent only, appends to `data/waitlist.jsonl`, gitignored). The free flow never stores answers.

### Education

The "I want to learn more" path has seven topics (`TIPS` in `app/i18n.py`): a zero-trust mindset, phone calls, messages and links, family and voices (cloned voices and video), investments, marketplaces, and your accounts. Each is an intro plus short sections. The premise is that there are no reliable tells any more: skilled fraudsters show no urgency, sound calm, know your details and may even tell you to hang up, so people are taught to judge what is asked, to verify through a channel they choose, to go to the bank in person when unsure and to talk to someone they trust. The content should be reviewed by a fraud specialist before launch.

### Languages

English, French and Dutch, chosen with the dropdown top right (remembered in the browser, defaulting to the browser language). Two places hold the text:
- `static/i18n.js`: all interface text, and the switch. Static page text uses `data-i18n` attributes.
- `app/i18n.py`: what the server writes: the verdict, the five plan steps, the fee terms and the protection tips. `POST /api/plan` takes `ui` (the language of the plan) and an optional `summary`, so switching language on a finished plan rebuilds it without calling the model again. `GET /api/tips` and `GET /api/terms` take `?lang=`.
- The two documents (claim letter, police report) have their own language, chosen on the last question. It starts as the interface language and is independent of it. Their templates are in `app/tools.py`.
- Case updates are stored as codes (`created`, `status:claim_sent`) and translated on the case page. A note written by the team is shown as written.

All translations are first drafts. Have native speakers review them together with the English originals, and a Belgian lawyer the legal wording in every language.

### Paid tier (pilot prototype)

After the plan, a victim with a strong or possible case can hand it over: details, fee terms and a typed-name mandate with explicit consent, then evidence upload. Cases we would decline are refused server-side.

- `app/cases.py`: SQLite (`data/cases.db`) and files (`data/evidence/<case>/`). Case id plus a random token (only its hash is stored). Evidence limited to 10 files of 10 MB, PDF/PNG/JPG/HEIC/TXT. Erasure deletes the row, events and files.
- `static/status.html`: the victim's case page, reached by a link `/status.html#<id>.<token>` (token in the URL fragment, sent as a header). Shows status and updates, adds files, deletes everything.
- `static/admin.html`: back office with the case list, details, the generated claim pack, evidence download and status updates (the note is shown to the victim). Disabled unless `FRAUD_AID_ADMIN_TOKEN` is set; one shared token, development only.
- Fee terms and mandate text live in `app/cases.py` (`TERMS`) and are marked as draft.
- `FRAUD_AID_DATA` moves the data directory (used by the tests).
- `static/`: one page, no build step. Newsreader, Aileron, black and white, accent `#9A2400` in the logo, selection and focus rings only. Logo is `static/logo.svg`.

## Run

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
ollama serve   # or the Ollama menu-bar app, with ministral-3:8b pulled
FRAUD_AID_ADMIN_TOKEN=choose-a-token venv/bin/uvicorn app.main:app --port 8000
```

The back office is at http://localhost:8000/admin.html (omit the variable to keep it disabled).

Open http://localhost:8000. Override the model with `FRAUD_AID_MODEL` and the Ollama address with `OLLAMA_URL`.

## Test

```bash
venv/bin/python tests/test_rules.py   # verdict rules
venv/bin/python tests/test_plan.py    # plan builder and documents, no LLM
venv/bin/python tests/test_cases.py   # paid tier: consent, tokens, evidence, back office, erasure
node tests/test_amount.js             # how typed amounts such as 444,00 or 1.234,56 are read
venv/bin/python tests/try_languages.py # live: the plan and the AI statement in each language (needs the server and Ollama)
venv/bin/python tests/try_plan.py     # live check against the running server and the local model
```

## Before this goes public

- Have a Belgian lawyer review the rules and the wording in `BASIS` and `HEADLINES` (`app/assess.py`). They are placeholders based on desk research (see `~/startup-ideas/victim-recovery-research.md`).
- Check whether taking a share of a recovery is regulated in Belgium (claims management or legal practice). A partner law firm may be required.
- Verify every contact detail and claim in the steps: Card Stop 078 170 170 and its opening hours, policeonweb.be and what fraud it accepts, ombudsfin.be, verdacht@safeonweb.be, fsma.be, the 13-month notice limit and the chargeback window wording.
- Waitlist emails need a proper privacy notice, retention policy and a real storage location.
- Building the plan takes about 10 to 15 seconds on the local model (one summary call).
- Add a lookup for the user's local police zone by postcode (the plan only points to the station and Police on Web).
- The paid tier is a development prototype. Before any real victim uses it: EU hosting, encryption at rest, a retention policy and data processing agreements; real admin accounts instead of a shared token; rate limiting; virus scanning of uploads; email notifications (none are sent today); lawyer-approved terms and mandate; and a decision on whether a typed name is enough as a signature.
- The local Ollama model is a demo setup. Do not send real victims' data to it on a laptop; use a hosted model under a data processing agreement or a properly secured self-hosted one.
- The local model sometimes invents a small detail in the statement it writes for the documents (for example "my account may be empty"). The code removes titles, markdown and repeated versions, and the page tells people to check every detail, but it is not a guarantee.
