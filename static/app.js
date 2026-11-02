const app = document.getElementById("app");

// Answers live in the browser only and are sent once, at the end, to build the plan.
let answers = {};
let trail = []; // indexes of the steps already shown, for Back

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  Object.assign(n, props);
  n.append(...kids);
  return n;
}

const opt = (value, title, sub) => ({ value, title, sub });

const YES_NO_UNSURE = [opt("yes", "Yes"), opt("no", "No"), opt("unclear", "Not sure")];

// ---- Steps -------------------------------------------------------------------------------

const STEPS = [
  {
    id: "country",
    ask: "Which country did this happen in?",
    type: "choice",
    options: [opt("BE", "Belgium"), opt("other", "Another country")],
  },
  { id: "amount", ask: "How much money did you lose?", type: "amount" },
  {
    id: "how",
    ask: "How did it happen?",
    type: "how",
    options: [
      opt("phone_call", "Someone called me"),
      opt("phishing_link", "A text, email or link"),
      opt("messaging", "A message on WhatsApp or social media"),
      opt("marketplace", "An online purchase or sale"),
      opt("investment", "An investment opportunity"),
      opt("romance", "Romance or a person in need"),
      opt("other", "Something else"),
    ],
  },
  {
    id: "impersonated",
    ask: "Who did they pretend to be?",
    type: "choice",
    when: (a) => ["phone_call", "phishing_link", "messaging"].includes(a.how),
    options: [
      opt("bank", "My bank"),
      opt("police", "The police or an authority"),
      opt("company", "A company or service", "Parcel, telecom, tax, a shop"),
      opt("relative", "A family member or friend"),
      opt("none", "Nobody in particular"),
    ],
  },
  {
    id: "authorised",
    ask: "Did you approve or send the payment yourself?",
    type: "choice",
    options: [
      opt("yes", "Yes, I approved it", "Even if I was pressured or tricked"),
      opt("no", "No, the money left my account without my approval"),
      opt("unclear", "I am not sure"),
    ],
  },
  {
    id: "method",
    ask: "How did you pay?",
    type: "choice",
    options: [opt("transfer", "Bank transfer"), opt("card", "Card payment"), opt("both", "Both"), opt("other", "Something else")],
  },
  {
    id: "when",
    ask: "When did it happen?",
    type: "choice",
    options: [opt("today", "Today"), opt("last_3_days", "In the last 3 days"), opt("last_month", "In the last month"), opt("older", "Longer ago")],
  },
  { id: "bank", ask: "Which bank are you with?", type: "bank" },
  { id: "extras", ask: "A few last things", type: "extras" },
];

const BANKS = ["KBC", "BNP Paribas Fortis", "Belfius", "ING", "Argenta", "Crelan", "Keytrade", "Revolut"];

// ---- Frame -------------------------------------------------------------------------------

function frame(stepIndex, ...content) {
  const total = STEPS.length;
  const top = el("div", { className: "top" });
  if (trail.length) {
    const back = el("button", { className: "back", type: "button" }, "← Back");
    back.addEventListener("click", goBack);
    top.append(back);
  }
  const progress = el("div", { className: "progress", ariaHidden: "true" }, el("i", { style: `width:${Math.round(((stepIndex + 1) / total) * 100)}%` }));
  top.append(progress);
  app.replaceChildren(top, el("section", { className: "screen" }, ...content));
  window.scrollTo(0, 0);
  const focusTarget = app.querySelector("[autofocus]") || app.querySelector("h2");
  focusTarget?.focus({ preventScroll: true });
}

function ask(text) {
  return el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, text));
}

function next(from) {
  let i = from + 1;
  while (i < STEPS.length && STEPS[i].when && !STEPS[i].when(answers)) i++;
  return i;
}

function goTo(i) {
  if (i >= STEPS.length) return buildPlan();
  render(i);
}

function advance(i) {
  trail.push(i);
  goTo(next(i));
}

function goBack() {
  const prev = trail.pop();
  if (prev === undefined) return start();
  render(prev);
}

// ---- Start -------------------------------------------------------------------------------

function start() {
  answers = {};
  trail = [];
  const hero = el(
    "div",
    { className: "ask" },
    el("img", { src: "/logo.svg", alt: "", width: 96, height: 96 }),
    el("h1", { className: "big" }, "Hi, I'm Suki."),
    el("p", { className: "sub" }, "Are you here because of a fraud incident, or to learn more?"),
  );
  const scammed = el("button", { className: "chip", type: "button" }, "I was scammed");
  const learn = el("button", { className: "chip", type: "button" }, "I want to learn more");
  scammed.addEventListener("click", () => render(0));
  learn.addEventListener("click", learnScreen);
  hero.append(el("div", { className: "chips" }, scammed, learn));
  app.replaceChildren(el("section", { className: "screen" }, hero));
  window.scrollTo(0, 0);
}

// ---- Renderers ---------------------------------------------------------------------------

function render(i) {
  const s = STEPS[i];
  if (s.type === "choice") return renderChoice(i, s);
  if (s.type === "amount") return renderAmount(i, s);
  if (s.type === "how") return renderHow(i, s);
  if (s.type === "bank") return renderBank(i, s);
  if (s.type === "extras") return renderExtras(i, s);
}

function renderChoice(i, s) {
  const list = el("div", { className: "options" });
  s.options.forEach((o) => {
    const b = el("button", { className: "opt", type: "button", ariaPressed: String(answers[s.id] === o.value) });
    b.append(el("span", {}, el("span", { className: "t" }, o.title), o.sub ? el("span", { className: "s" }, o.sub) : ""));
    b.addEventListener("click", () => {
      answers[s.id] = o.value;
      if (s.id === "country" && o.value === "other") return otherCountry();
      advance(i);
    });
    list.append(b);
  });
  frame(i, ask(s.ask), list);
}

function renderAmount(i, s) {
  const input = el("input", { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "0", ariaLabel: "Amount lost in euros", autofocus: true });
  if (answers.amount_eur) input.value = answers.amount_eur;
  const go = el("button", { className: "button", type: "submit", disabled: !input.value }, "Continue");
  const unsure = el("button", { className: "button ghost", type: "button" }, "I am not sure");
  input.addEventListener("input", () => (go.disabled = !(Number(input.value) > 0)));
  unsure.addEventListener("click", () => {
    answers.amount_eur = null;
    advance(i);
  });
  const form = el("form", {}, el("div", { className: "money" }, el("span", {}, "€"), input), el("div", { className: "row" }, go, unsure));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!(Number(input.value) > 0)) return;
    answers.amount_eur = Number(input.value);
    advance(i);
  });
  frame(i, ask(s.ask), form);
  input.focus();
}

function renderHow(i, s) {
  const list = el("div", { className: "options" });
  const go = el("button", { className: "button", type: "submit", disabled: !answers.how }, "Continue");
  s.options.forEach((o) => {
    const b = el("button", { className: "opt", type: "button", ariaPressed: String(answers.how === o.value) });
    b.append(el("span", { className: "t" }, o.title));
    b.addEventListener("click", () => {
      answers.how = o.value;
      list.querySelectorAll(".opt").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      go.disabled = false;
    });
    list.append(b);
  });
  const text = el("textarea", { className: "text", rows: 4, maxLength: 3000, placeholder: "What happened, in your own words. The more detail, the better your documents.", id: "free" });
  text.value = answers.free_text || "";
  const field = el("div", { className: "field" }, el("label", { htmlFor: "free" }, "Tell us in your own words (optional)"), text);
  const form = el("form", {}, list, field, el("div", { className: "row" }, go));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!answers.how) return;
    answers.free_text = text.value.trim();
    advance(i);
  });
  frame(i, ask(s.ask), form);
}

function renderBank(i, s) {
  const grid = el("div", { className: "grid" });
  const other = el("input", { className: "text", type: "text", maxLength: 60, placeholder: "Type the name of your bank", ariaLabel: "Bank name" });
  const otherWrap = el("div", { className: "field" }, other);
  otherWrap.hidden = true;
  const go = el("button", { className: "button", type: "submit", disabled: true }, "Continue");
  let chosen = answers.bank || "";
  const sync = () => {
    grid.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.v === (BANKS.includes(chosen) ? chosen : chosen ? "Other" : ""))));
    otherWrap.hidden = !(chosen && !BANKS.includes(chosen));
    go.disabled = !chosen.trim();
  };
  [...BANKS, "Other"].forEach((b) => {
    const c = el("button", { className: "chip", type: "button", ariaPressed: "false" }, b);
    c.dataset.v = b;
    c.addEventListener("click", () => {
      if (b === "Other") {
        chosen = BANKS.includes(chosen) ? "" : chosen;
        otherWrap.hidden = false;
        other.focus();
        grid.querySelectorAll(".chip").forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
        go.disabled = !other.value.trim();
        return;
      }
      chosen = b;
      sync();
    });
    grid.append(c);
  });
  other.addEventListener("input", () => {
    chosen = other.value.trim();
    go.disabled = !chosen;
  });
  const form = el("form", {}, grid, otherWrap, el("div", { className: "row" }, go));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!chosen.trim()) return;
    answers.bank = chosen.trim();
    advance(i);
  });
  frame(i, ask(s.ask), form);
  if (chosen) {
    if (!BANKS.includes(chosen)) other.value = chosen;
    sync();
  }
}

function pillGroup(name, legend, options, current) {
  const pills = el("div", { className: "pills" });
  options.forEach((o) => {
    const input = el("input", { type: "radio", name, value: o.value, checked: current === o.value });
    pills.append(el("label", { className: "pill" }, input, el("span", {}, o.title)));
  });
  const fs = el("fieldset", {}, el("legend", {}, legend), pills);
  return el("div", { className: "field" }, fs);
}

function renderExtras(i, s) {
  const yn = [opt("yes", "Yes"), opt("no", "No")];
  const form = el("form", {});
  form.append(
    pillGroup("shared_credentials", "Did you give anyone codes, card details or an itsme approval?", YES_NO_UNSURE, answers.shared_credentials || "unclear"),
    pillGroup("remote_access", "Did you install an app or let someone control your phone or computer?", YES_NO_UNSURE, answers.remote_access || "unclear"),
    pillGroup("told_bank", "Have you already told your bank?", yn, answers.told_bank === true ? "yes" : "no"),
    pillGroup("told_police", "Have you already reported it to the police?", yn, answers.told_police === true ? "yes" : "no"),
  );
  const details = el("input", { className: "text", type: "text", maxLength: 500, id: "scammer", placeholder: "IBAN, phone number, website or profile name" });
  details.value = answers.scammer_details || "";
  form.append(el("div", { className: "field" }, el("label", { htmlFor: "scammer" }, "Anything you know about the scammer (optional)"), details));
  form.append(
    pillGroup("language", "Language for your letter and police report", [opt("nl", "Nederlands"), opt("fr", "Français"), opt("en", "English")], answers.language || "nl"),
  );
  form.append(el("div", { className: "row" }, el("button", { className: "button", type: "submit" }, "Show my plan")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(form);
    answers.shared_credentials = f.get("shared_credentials");
    answers.remote_access = f.get("remote_access");
    answers.told_bank = f.get("told_bank") === "yes";
    answers.told_police = f.get("told_police") === "yes";
    answers.scammer_details = details.value.trim();
    answers.language = f.get("language");
    advance(i);
  });
  frame(i, ask(s.ask), form);
}

function otherCountry() {
  const email = el("input", { className: "text", type: "email", placeholder: "you@example.com", ariaLabel: "Email address", required: true });
  const box = el("input", { type: "checkbox", required: true });
  const msg = el("p", { className: "hint" });
  const go = el("button", { className: "button", type: "submit" }, "Notify me");
  const form = el(
    "form",
    {},
    el("div", { className: "field" }, email),
    el("label", { className: "consent field" }, box, "I agree that Fraud Aid stores my email to tell me when my country is available."),
    el("div", { className: "row" }, go),
    msg,
  );
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    go.disabled = true;
    const r = await fetch("/api/waitlist", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: email.value, consent: box.checked, note: "country not supported" }) }).catch(() => null);
    msg.textContent = r && r.ok ? "Thank you. We will email you when we open." : "That did not work. Please check your email address.";
    go.disabled = !!(r && r.ok);
  });
  trail.push(0);
  frame(0, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, "Fraud Aid works in Belgium for now."), el("p", { className: "sub" }, "Banking rules differ per country, so we only give advice where we have checked them. Leave your email and we will tell you when yours is ready. In the meantime, call your bank and report the fraud to your local police today.")), form);
}

// ---- Learn -------------------------------------------------------------------------------

const TOPICS = [
  ["phone_calls", "Phone calls"],
  ["messages_and_links", "Messages and links"],
  ["elderly_relatives", "Protecting parents or grandparents"],
  ["investments", "Investments"],
  ["marketplaces", "Buying and selling online"],
  ["your_accounts", "Securing my accounts"],
];

function learnScreen() {
  const list = el("div", { className: "options" });
  TOPICS.forEach(([key, title]) => {
    const b = el("button", { className: "opt", type: "button" }, el("span", { className: "t" }, title));
    b.addEventListener("click", () => tipsScreen(key, title));
    list.append(b);
  });
  const back = el("button", { className: "back", type: "button" }, "← Back");
  back.addEventListener("click", start);
  app.replaceChildren(el("div", { className: "top" }, back), el("section", { className: "screen" }, ask("What would you like to learn about?"), list));
  window.scrollTo(0, 0);
}

async function tipsScreen(key, title) {
  const r = await fetch("/api/tips").catch(() => null);
  const tips = r && r.ok ? (await r.json())[key] : null;
  const ul = el("ul", { className: "tips" });
  (tips || ["Something went wrong. Please try again."]).forEach((t) => ul.append(el("li", {}, t)));
  const back = el("button", { className: "back", type: "button" }, "← All topics");
  back.addEventListener("click", learnScreen);
  app.replaceChildren(el("div", { className: "top" }, back), el("section", { className: "screen" }, ask(title), ul));
  window.scrollTo(0, 0);
}

// ---- Plan --------------------------------------------------------------------------------

const euro = (n) => new Intl.NumberFormat("en-BE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
const LEVELS = { strong: "Strong position", possible: "Possible claim", unlikely: "Unlikely", unclear: "More information needed" };

async function buildPlan() {
  app.replaceChildren(
    el(
      "section",
      { className: "screen" },
      el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, "Putting your plan together"), el("span", { className: "typing", ariaHidden: "true" }, el("i"), el("i"), el("i")), el("p", { className: "hint" }, "This takes up to a minute. Your answers are not saved.")),
    ),
  );
  window.scrollTo(0, 0);
  try {
    const body = { ...answers, amount_eur: answers.amount_eur || null };
    const r = await fetch("/api/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error("bad");
    showPlan(await r.json());
  } catch {
    const retry = el("button", { className: "button", type: "button" }, "Try again");
    retry.addEventListener("click", buildPlan);
    app.replaceChildren(el("section", { className: "screen" }, el("div", { className: "ask" }, el("h2", { className: "big" }, "Something went wrong."), el("p", { className: "sub" }, "Your answers are still here. If it keeps failing, call Card Stop on 078 170 170 and your bank right away."), retry)));
  }
}

function docBlock(doc) {
  const copy = el("button", { type: "button" }, "Copy");
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(doc.text);
      copy.textContent = "Copied";
    } catch {
      copy.textContent = "Select and copy";
    }
    setTimeout(() => (copy.textContent = "Copy"), 2000);
  });
  return el(
    "div",
    { className: "doc" },
    el("header", {}, el("span", { className: "label" }, doc.title), copy),
    el("pre", {}, doc.text),
    el("p", { className: "note" }, "Check every detail and fill in the [brackets] before you send or file it."),
  );
}

function showPlan(plan) {
  lastPlan = plan;
  const v = plan.verdict;
  const head = el("div", { className: "head" }, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, "Here is your plan")));
  const wrap = el("div", { className: "plan" }, head);

  if (plan.urgent) wrap.append(el("p", { className: "urgent" }, "It just happened, so the next hour matters most. Start with step 1."));

  const verdict = el("div", { className: "verdict" }, el("p", { className: "label quiet" }, LEVELS[v.level]), el("p", { className: "headline" }, v.headline));
  if (v.up_to_eur) verdict.append(el("p", { className: "amount" }, el("small", {}, "You may be entitled to up to, non-binding"), euro(v.up_to_eur)));
  verdict.append(el("p", { className: "basis" }, v.basis));
  wrap.append(verdict);

  const ol = el("ol", { className: "steps" });
  plan.steps.forEach((s, idx) => {
    const body = el("div", {}, el("h3", {}, s.title));
    s.intro.forEach((t) => body.append(el("p", {}, t)));
    if (s.bullets.length) {
      const ul = el("ul");
      s.bullets.forEach((t) => ul.append(el("li", {}, t)));
      body.append(ul);
    }
    if (s.actions.length) {
      const row = el("div", { className: "actions" });
      s.actions.forEach((a) => row.append(el("a", { className: "button ghost", href: a.href, target: a.href.startsWith("http") ? "_blank" : "_self", rel: "noopener" }, a.label)));
      body.append(row);
    }
    if (s.doc) body.append(docBlock(s.doc));
    ol.append(el("li", { className: "step" }, el("span", { className: "n" }, String(idx + 1)), body));
  });
  wrap.append(ol);

  if (plan.can_offer_help) wrap.append(helpBox());

  const row = el("div", { className: "row noprint" });
  const print = el("button", { className: "button ghost", type: "button" }, "Print or save as PDF");
  print.addEventListener("click", () => window.print());
  const again = el("button", { className: "button ghost", type: "button" }, "Start over");
  again.addEventListener("click", start);
  row.append(print, again);
  wrap.append(row);

  app.replaceChildren(el("section", { className: "screen" }, wrap));
  window.scrollTo(0, 0);
  wrap.querySelector("h2")?.focus({ preventScroll: true });
}

// ---- Hand the case over to Fraud Aid ---------------------------------------------------------

let lastPlan = null;
let contact = {};
let caseRef = null;

function helpBox() {
  const go = el("button", { className: "button", type: "button" }, "Let Fraud Aid handle it");
  go.addEventListener("click", detailsScreen);
  return el(
    "div",
    { className: "help" },
    el("h3", {}, "Want us to handle it?"),
    el("p", {}, "Give us your case and we process the claim for you: we deal with your bank, follow up and escalate. You pay 20% plus VAT of what you recover, and nothing if you recover nothing."),
    el("div", { className: "row", style: "margin-top:18px" }, go),
  );
}

function sideScreen(backFn, ...content) {
  const top = el("div", { className: "top" });
  if (backFn) {
    const back = el("button", { className: "back", type: "button" }, "← Back");
    back.addEventListener("click", backFn);
    top.append(back);
  }
  app.replaceChildren(top, el("section", { className: "screen" }, ...content));
  window.scrollTo(0, 0);
  app.querySelector("h2")?.focus({ preventScroll: true });
}

function field(id, label, props = {}) {
  const input = el("input", { className: "text", id, name: id, ...props });
  return [el("div", { className: "field" }, el("label", { htmlFor: id }, label), input), input];
}

async function errorText(r) {
  const body = await r.json().catch(() => ({}));
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail) && body.detail[0]) {
    const d = body.detail[0];
    return `${(d.loc || []).slice(-1)[0] || "Input"}: ${String(d.msg || "invalid").replace(/^Value error, /, "")}`;
  }
  return "Something went wrong. Please try again.";
}

function detailsScreen() {
  const [fName, name] = field("full_name", "Full name", { autocomplete: "name", required: true, maxLength: 100, value: contact.full_name || "" });
  const [fEmail, email] = field("email", "Email", { type: "email", autocomplete: "email", required: true, value: contact.email || "" });
  const [fPhone, phone] = field("phone", "Phone", { type: "tel", autocomplete: "tel", required: true, maxLength: 30, value: contact.phone || "" });
  const [fAddr, addr] = field("address", "Address", { autocomplete: "street-address", required: true, maxLength: 200, placeholder: "Street, number, postcode, city", value: contact.address || "" });
  const [fIban, iban] = field("iban", "IBAN of the account that was charged", { required: true, maxLength: 40, placeholder: "BE00 0000 0000 0000", value: contact.iban || "" });
  const err = el("p", { className: "error", hidden: true, role: "alert" });
  const form = el("form", {}, fName, fEmail, fPhone, fAddr, fIban, err, el("div", { className: "row" }, el("button", { className: "button", type: "submit" }, "Continue")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    contact = { full_name: name.value.trim(), email: email.value.trim(), phone: phone.value.trim(), address: addr.value.trim(), iban: iban.value.trim() };
    termsScreen();
  });
  sideScreen(() => showPlan(lastPlan), ask("Your details"), el("p", { className: "sub", style: "margin-top:14px" }, "We need these to claim on your behalf. They are stored only if you send us your case on the next screen."), form);
  name.focus();
}

async function termsScreen() {
  const t = await fetch("/api/terms").then((r) => r.json()).catch(() => null);
  if (!t) return sideScreen(detailsScreen, ask("Something went wrong"), el("p", { className: "sub" }, "Please go back and try again."));
  const list = (items) => el("ul", {}, ...items.map((x) => el("li", {}, x)));
  const sec = (title, node) => el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, title), node);

  const sign = el("input", { className: "text", id: "signature", required: true, maxLength: 100, autocomplete: "off", placeholder: "Type your full name" });
  const box = (name, text, required = true) => {
    const input = el("input", { type: "checkbox", name, required });
    return [el("label", { className: "consent" }, input, text), input];
  };
  const [cPrivacy, iPrivacy] = box("privacy", t.privacy);
  const [cTerms, iTerms] = box("terms", "I accept the fee and the terms above.");
  const [cMandate, iMandate] = box("mandate", "I give Fraud Aid the authorisation above.");
  const [cShare, iShare] = box("share", t.share, false);
  const err = el("p", { className: "error", hidden: true, role: "alert" });
  const go = el("button", { className: "button", type: "submit" }, "Send my case");

  const form = el(
    "form",
    {},
    el("p", { className: "urgent" }, t.draft_notice),
    sec("What it costs", list(t.fee)),
    sec("What we do", list(t.we_do)),
    sec("What you do", list(t.you_do)),
    sec("Your rights", list(t.rights)),
    sec("Authorisation", el("p", { className: "mandate" }, t.mandate)),
    el("div", { className: "field" }, el("label", { htmlFor: "signature" }, "Sign by typing your full name"), sign),
    el("div", { className: "checks" }, cPrivacy, cTerms, cMandate, cShare),
    err,
    el("div", { className: "row" }, go),
  );
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.hidden = true;
    go.disabled = true;
    go.textContent = "Sending...";
    const body = {
      answers: { ...answers, amount_eur: answers.amount_eur || null },
      summary: lastPlan ? lastPlan.summary : "",
      contact,
      consent: { privacy: iPrivacy.checked, terms: iTerms.checked, mandate: iMandate.checked, signature_name: sign.value.trim(), share_intel: iShare.checked },
    };
    try {
      const r = await fetch("/api/cases", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (!r.ok) throw new Error(await errorText(r));
      const j = await r.json();
      caseRef = { id: j.case_id, token: j.token };
      evidenceScreen();
    } catch (ex) {
      err.textContent = ex.message;
      err.hidden = false;
      go.disabled = false;
      go.textContent = "Send my case";
    }
  });
  sideScreen(detailsScreen, ask("Fee and authorisation"), el("div", { style: "margin-top:24px" }, form));
}

function evidenceScreen() {
  const list = el("ul", { className: "uploads" });
  const pick = el("input", { type: "file", multiple: true, accept: ".pdf,.png,.jpg,.jpeg,.heic,.txt", id: "files", className: "text" });
  const err = el("p", { className: "error", hidden: true, role: "alert" });
  pick.addEventListener("change", async () => {
    err.hidden = true;
    for (const f of [...pick.files]) {
      const li = el("li", {}, `${f.name} `, el("span", { className: "quiet" }, "uploading..."));
      list.append(li);
      const fd = new FormData();
      fd.append("file", f);
      const r = await fetch(`/api/cases/${caseRef.id}/evidence`, { method: "POST", headers: { "X-Case-Token": caseRef.token }, body: fd }).catch(() => null);
      li.lastChild.textContent = r && r.ok ? "added" : "failed";
      if (!r || !r.ok) {
        err.textContent = r ? await errorText(r) : "Upload failed. Please try again.";
        err.hidden = false;
      }
    }
    pick.value = "";
  });
  const done = el("button", { className: "button", type: "button" }, "Finish");
  done.addEventListener("click", doneScreen);
  sideScreen(
    null,
    ask("Add your evidence"),
    el("p", { className: "sub", style: "margin-top:14px" }, "Screenshots of the messages, your bank statement, the transfer confirmation, the call log and your police report. PDF, PNG, JPG, HEIC or TXT, up to 10 files of 10 MB. You can add more later."),
    el("div", { className: "field" }, el("label", { htmlFor: "files" }, "Choose files"), pick),
    list,
    err,
    el("div", { className: "row" }, done),
  );
}

function doneScreen() {
  const link = `${location.origin}/status.html#${caseRef.id}.${caseRef.token}`;
  const copy = el("button", { className: "button ghost", type: "button" }, "Copy link");
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(link);
      copy.textContent = "Copied";
    } catch {
      copy.textContent = "Select and copy below";
    }
  });
  sideScreen(
    null,
    ask("We have your case."),
    el("p", { className: "ref" }, caseRef.id),
    el("p", { className: "sub" }, `We will review it and contact you at ${contact.email}. Keep this link: it is the only way back to your case page, where you can see the status, add files or delete everything.`),
    el("p", { className: "linkbox" }, link),
    el("div", { className: "row" }, copy, el("a", { className: "button", href: link }, "Open my case page")),
  );
}

start();
