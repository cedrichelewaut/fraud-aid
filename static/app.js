const app = document.getElementById("app");

// Answers live in the browser only and are sent once, at the end, to build the plan.
let answers = {};
let trail = []; // indexes of the steps already shown, for Back
let view = null; // how to draw the current screen again, for when the language changes
let lastPlan = null;
let contact = {};
let caseRef = null;
let handoverFrom = "plan"; // where the hand-over was started, so Back goes to the right place
let planPromise = null; // the plan is built in the background while someone fills in the hand-over forms

const reading = (on) => document.body.classList.toggle("reading", on);

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  Object.assign(n, props);
  n.append(...kids);
  return n;
}

const opt = (value, key, subKey) => ({ value, key, subKey });
const YES_NO_UNSURE = () => [opt("yes", "yes"), opt("no", "no"), opt("unclear", "unsure")];

// ---- Steps -------------------------------------------------------------------------------

const STEPS = [
  { id: "country", ask: "q_country", type: "choice", options: [opt("BE", "country_be"), opt("other", "country_other")] },
  { id: "amount", ask: "q_amount", type: "amount" },
  {
    id: "how",
    ask: "q_how",
    type: "how",
    options: ["phone_call", "phishing_link", "messaging", "marketplace", "investment", "romance", "other"].map((v) => opt(v, "how_" + v)),
  },
  {
    id: "impersonated",
    ask: "q_impersonated",
    type: "choice",
    when: (a) => ["phone_call", "phishing_link", "messaging"].includes(a.how),
    options: [opt("bank", "imp_bank"), opt("police", "imp_police"), opt("company", "imp_company", "imp_company_sub"), opt("relative", "imp_relative"), opt("none", "imp_none")],
  },
  {
    id: "authorised",
    ask: "q_authorised",
    type: "choice",
    options: [opt("yes", "auth_yes", "auth_yes_sub"), opt("no", "auth_no"), opt("unclear", "auth_unclear")],
  },
  { id: "method", ask: "q_method", type: "choice", options: [opt("transfer", "m_transfer"), opt("card", "m_card"), opt("both", "m_both"), opt("other", "m_other")] },
  { id: "when", ask: "q_when", type: "choice", options: ["today", "last_3_days", "last_month", "older"].map((v) => opt(v, "w_" + v)) },
  { id: "bank", ask: "q_bank", type: "bank" },
  { id: "extras", ask: "q_extras", type: "extras" },
];

const BANKS = ["KBC", "BNP Paribas Fortis", "Belfius", "ING", "Argenta", "Crelan", "Keytrade", "Revolut"];

// ---- Frame -------------------------------------------------------------------------------

function frame(stepIndex, ...content) {
  reading(false);
  const top = el("div", { className: "top" });
  if (trail.length) {
    const back = el("button", { className: "back", type: "button" }, t("back"));
    back.addEventListener("click", goBack);
    top.append(back);
  }
  const progress = el("div", { className: "progress", ariaHidden: "true" }, el("i", { style: `width:${Math.round(((stepIndex + 1) / STEPS.length) * 100)}%` }));
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
  if (i >= STEPS.length) return afterQuestions();
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
  lastPlan = null;
  showStart();
}

function showStart() {
  view = showStart;
  reading(false);
  const hero = el(
    "div",
    { className: "ask" },
    el("img", { src: "/logo.svg", alt: "", width: 96, height: 96 }),
    el("h1", { className: "big" }, t("start_h1")),
    el("p", { className: "sub" }, t("start_sub")),
  );
  const scammed = el("button", { className: "chip", type: "button" }, t("chip_scammed"));
  const learn = el("button", { className: "chip", type: "button" }, t("chip_learn"));
  scammed.addEventListener("click", () => render(0));
  learn.addEventListener("click", learnScreen);
  hero.append(el("div", { className: "chips" }, scammed, learn));
  app.replaceChildren(el("section", { className: "screen" }, hero));
  window.scrollTo(0, 0);
}

// ---- Renderers ---------------------------------------------------------------------------

function render(i) {
  view = () => render(i);
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
    b.append(el("span", {}, el("span", { className: "t" }, t(o.key)), o.subKey ? el("span", { className: "s" }, t(o.subKey)) : ""));
    b.addEventListener("click", () => {
      answers[s.id] = o.value;
      if (s.id === "country" && o.value === "other") return otherCountry();
      advance(i);
    });
    list.append(b);
  });
  frame(i, ask(t(s.ask)), list);
}

function renderAmount(i, s) {
  const input = el("input", { type: "text", inputMode: "decimal", autocomplete: "off", placeholder: "0,00", ariaLabel: t("amount_aria"), autofocus: true });
  input.value = answers._amountText ?? (answers.amount_eur ? String(answers.amount_eur).replace(".", ",") : "");
  const valid = () => {
    const n = parseAmount(input.value);
    return n > 0 && n < 10000000;
  };
  const go = el("button", { className: "button", type: "submit", disabled: !valid() }, t("continue"));
  const unsure = el("button", { className: "button ghost", type: "button" }, t("not_sure"));
  input.addEventListener("input", () => {
    answers._amountText = input.value;
    go.disabled = !valid();
  });
  unsure.addEventListener("click", () => {
    answers.amount_eur = null;
    advance(i);
  });
  const form = el("form", {}, el("div", { className: "money" }, el("span", {}, "€"), input), el("div", { className: "row" }, go, unsure));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!valid()) return;
    answers.amount_eur = parseAmount(input.value);
    advance(i);
  });
  frame(i, ask(t(s.ask)), form);
  input.focus();
}

function renderHow(i, s) {
  // Clicking an option continues at once. "Continue" is only for people who write their own account.
  const text = el("textarea", { className: "text", rows: 4, maxLength: 3000, placeholder: t("free_ph"), id: "free" });
  text.value = answers.free_text || "";
  const go = el("button", { className: "button", type: "submit", disabled: !text.value.trim() && !answers.how }, t("continue"));
  const proceed = (how) => {
    answers.how = how;
    answers.free_text = text.value.trim();
    advance(i);
  };

  const list = el("div", { className: "options" });
  s.options.forEach((o) => {
    const b = el("button", { className: "opt", type: "button", ariaPressed: String(answers.how === o.value) });
    b.append(el("span", { className: "t" }, t(o.key)));
    b.addEventListener("click", () => proceed(o.value));
    list.append(b);
  });

  text.addEventListener("input", () => {
    answers.free_text = text.value;
    go.disabled = !text.value.trim() && !answers.how;
  });
  const field = el("div", { className: "field" }, el("label", { htmlFor: "free" }, t("free_label")), text);
  const form = el("form", {}, list, field, el("div", { className: "row" }, go));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (text.value.trim() || answers.how) proceed(answers.how || "other");
  });
  frame(i, ask(t(s.ask)), form);
}

function renderBank(i, s) {
  const grid = el("div", { className: "grid" });
  const other = el("input", { className: "text", type: "text", maxLength: 60, placeholder: t("bank_ph"), ariaLabel: t("bank_aria") });
  const otherWrap = el("div", { className: "field" }, other);
  otherWrap.hidden = true;
  const go = el("button", { className: "button", type: "submit", disabled: true }, t("continue"));
  let chosen = answers.bank || "";
  const sync = () => {
    grid.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.v === (BANKS.includes(chosen) ? chosen : chosen ? "Other" : ""))));
    otherWrap.hidden = !(chosen && !BANKS.includes(chosen));
    go.disabled = !chosen.trim();
  };
  [...BANKS, "Other"].forEach((b) => {
    const c = el("button", { className: "chip", type: "button", ariaPressed: "false" }, b === "Other" ? t("bank_other") : b);
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
  frame(i, ask(t(s.ask)), form);
  if (chosen) {
    if (!BANKS.includes(chosen)) other.value = chosen;
    sync();
  }
}

function pillGroup(name, legend, options, current) {
  const pills = el("div", { className: "pills" });
  options.forEach((o) => {
    const input = el("input", { type: "radio", name, value: o.value, checked: current === o.value });
    pills.append(el("label", { className: "pill" }, input, el("span", {}, o.label ?? t(o.key))));
  });
  return el("div", { className: "field" }, el("fieldset", {}, el("legend", {}, legend), pills));
}

function renderExtras(i, s) {
  const yn = [opt("yes", "yes"), opt("no", "no")];
  const form = el("form", {});
  form.append(
    pillGroup("shared_credentials", t("x_shared"), YES_NO_UNSURE(), answers.shared_credentials || "unclear"),
    pillGroup("remote_access", t("x_remote"), YES_NO_UNSURE(), answers.remote_access || "unclear"),
    pillGroup("told_bank", t("x_told_bank"), yn, answers.told_bank === true ? "yes" : "no"),
    pillGroup("told_police", t("x_told_police"), yn, answers.told_police === true ? "yes" : "no"),
  );
  const details = el("input", { className: "text", type: "text", maxLength: 500, id: "scammer", placeholder: t("x_scammer_ph") });
  details.value = answers.scammer_details || "";
  form.append(el("div", { className: "field" }, el("label", { htmlFor: "scammer" }, t("x_scammer")), details));
  // The language of the two documents. It starts as the language you are using the site in.
  form.append(
    pillGroup(
      "language",
      t("x_language"),
      [{ value: "nl", label: "Nederlands" }, { value: "fr", label: "Français" }, { value: "en", label: "English" }],
      answers.language || LANG,
    ),
  );
  form.append(el("div", { className: "row" }, el("button", { className: "button", type: "submit" }, t("show_plan"))));
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
  frame(i, ask(t(s.ask)), form);
}

function otherCountry() {
  view = otherCountry;
  const email = el("input", { className: "text", type: "email", placeholder: t("email_ph"), ariaLabel: t("email_aria"), required: true });
  const box = el("input", { type: "checkbox", required: true });
  const msg = el("p", { className: "hint" });
  const go = el("button", { className: "button", type: "submit" }, t("notify_me"));
  const form = el("form", {}, el("div", { className: "field" }, email), el("label", { className: "consent field" }, box, t("oc_consent")), el("div", { className: "row" }, go), msg);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    go.disabled = true;
    const r = await fetch("/api/waitlist", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: email.value, consent: box.checked, note: "country not supported" }) }).catch(() => null);
    msg.textContent = r && r.ok ? t("oc_ok") : t("oc_fail");
    go.disabled = !!(r && r.ok);
  });
  if (trail[trail.length - 1] !== 0) trail.push(0);
  frame(0, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, t("oc_title")), el("p", { className: "sub" }, t("oc_sub"))), form);
}

// ---- Learn -------------------------------------------------------------------------------

const TOPICS = ["zero_trust", "phone_calls", "messages_and_links", "family_voices", "investments", "marketplaces", "your_accounts"];

function learnScreen() {
  view = learnScreen;
  reading(false);
  const list = el("div", { className: "options" });
  TOPICS.forEach((key) => {
    const b = el("button", { className: "opt", type: "button" }, el("span", { className: "t" }, t("topic_" + key)));
    b.addEventListener("click", () => tipsScreen(key));
    list.append(b);
  });
  const back = el("button", { className: "back", type: "button" }, t("back"));
  back.addEventListener("click", start);
  app.replaceChildren(el("div", { className: "top" }, back), el("section", { className: "screen" }, ask(t("learn_q")), list));
  window.scrollTo(0, 0);
}

async function tipsScreen(key) {
  view = () => tipsScreen(key);
  reading(false);
  const r = await fetch(`/api/tips?lang=${LANG}`).catch(() => null);
  const topic = r && r.ok ? (await r.json())[key] : null;
  const body = el("div", { className: "tipsbody" });
  if (topic) {
    body.append(el("p", { className: "sub tipintro" }, topic.intro));
    topic.items.forEach((it) => body.append(el("div", { className: "tip" }, el("h3", {}, it.h), el("p", {}, it.p))));
  } else {
    body.append(el("p", { className: "sub" }, t("went_wrong")));
  }
  const cta = el("button", { className: "chip", type: "button" }, t("tips_cta"));
  cta.addEventListener("click", () => {
    answers = {};
    trail = [];
    lastPlan = null;
    render(0);
  });
  const back = el("button", { className: "back", type: "button" }, t("all_topics"));
  back.addEventListener("click", learnScreen);
  app.replaceChildren(el("div", { className: "top" }, back), el("section", { className: "screen" }, ask(t("topic_" + key)), body, el("div", { className: "row" }, cta)));
  window.scrollTo(0, 0);
}

// ---- Plan --------------------------------------------------------------------------------

const euro = (n) => new Intl.NumberFormat(LANG === "en" ? "en-BE" : LANG === "fr" ? "fr-BE" : "nl-BE", { style: "currency", currency: "EUR", minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n);

function planBody(reuseSummary) {
  return { ...answers, _amountText: undefined, amount_eur: answers.amount_eur || null, ui: LANG, summary: reuseSummary && lastPlan ? lastPlan.summary : undefined };
}

async function buildPlan() {
  view = () => reloadPlan();
  reading(false);
  app.replaceChildren(
    el(
      "section",
      { className: "screen" },
      el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, t("loading_title")), el("span", { className: "typing", ariaHidden: "true" }, el("i"), el("i"), el("i")), el("p", { className: "hint" }, t("loading_hint"))),
    ),
  );
  window.scrollTo(0, 0);
  try {
    const r = await fetch("/api/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(planBody(false)) });
    if (!r.ok) throw new Error("bad");
    showPlan(await r.json());
  } catch {
    const retry = el("button", { className: "button", type: "button" }, t("try_again"));
    retry.addEventListener("click", buildPlan);
    app.replaceChildren(el("section", { className: "screen" }, el("div", { className: "ask" }, el("h2", { className: "big" }, t("err_title")), el("p", { className: "sub" }, t("err_sub")), retry)));
  }
}

// Switching language on the plan: the same answers and the same statement, so no new AI call.
async function reloadPlan() {
  if (!lastPlan) return buildPlan();
  const r = await fetch("/api/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(planBody(true)) }).catch(() => null);
  if (r && r.ok) showPlan(await r.json());
}

function docBlock(doc) {
  const copy = el("button", { type: "button" }, t("copy"));
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(doc.text);
      copy.textContent = t("copied");
    } catch {
      copy.textContent = t("copy_select");
    }
    setTimeout(() => (copy.textContent = t("copy")), 2000);
  });
  return el("div", { className: "doc" }, el("header", {}, el("span", { className: "label" }, doc.title), copy), el("pre", {}, doc.text), el("p", { className: "note" }, t("doc_note")));
}

function showPlan(plan) {
  lastPlan = plan;
  view = () => reloadPlan();
  reading(true);
  const v = plan.verdict;
  const head = el("div", { className: "head" }, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big", tabIndex: -1 }, t("plan_title"))));
  const wrap = el("div", { className: "plan" }, head);

  if (plan.urgent) wrap.append(el("p", { className: "urgent" }, t("urgent")));

  const verdict = el("div", { className: "verdict" }, el("p", { className: "label quiet" }, t("level_" + v.level)), el("p", { className: "headline" }, v.headline));
  if (v.up_to_eur) verdict.append(el("p", { className: "amount" }, el("small", {}, t("amount_label")), euro(v.up_to_eur)));
  verdict.append(el("p", { className: "basis" }, v.basis));
  wrap.append(verdict);

  const ol = el("ol", { className: "steps" });
  plan.steps.forEach((s, idx) => {
    const body = el("div", {}, el("h3", {}, s.title));
    s.intro.forEach((x) => body.append(el("p", {}, x)));
    if (s.bullets.length) {
      const ul = el("ul");
      s.bullets.forEach((x) => ul.append(el("li", {}, x)));
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

  if (plan.can_offer_help && !caseRef) wrap.append(helpBox());

  const row = el("div", { className: "row noprint" });
  const print = el("button", { className: "button ghost", type: "button" }, t("print"));
  print.addEventListener("click", () => window.print());
  const again = el("button", { className: "button ghost", type: "button" }, t("start_over"));
  again.addEventListener("click", start);
  row.append(print, again);
  wrap.append(row);

  app.replaceChildren(el("section", { className: "screen" }, wrap));
  window.scrollTo(0, 0);
  wrap.querySelector("h2")?.focus({ preventScroll: true });
}

// ---- Do it yourself, or let Fraud Aid help ----------------------------------------------------

// Fraud Aid only offers to take cases it can take on. Everyone else goes straight to their own plan.
async function afterQuestions() {
  view = afterQuestions;
  const r = await fetch("/api/verdict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(planBody(false)) }).catch(() => null);
  const eligible = r && r.ok && (await r.json()).can_offer_help;
  if (eligible) choiceScreen();
  else buildPlan();
}

function startPlanFetch() {
  if (lastPlan || planPromise) return;
  planPromise = fetch("/api/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(planBody(false)) })
    .then((r) => (r.ok ? r.json() : null))
    .then((p) => {
      if (p) lastPlan = p;
      return p;
    })
    .catch(() => null)
    .finally(() => (planPromise = null));
}

function choiceScreen() {
  view = choiceScreen;
  const card = (titleKey, textKey) => el("button", { className: "opt", type: "button" }, el("span", {}, el("span", { className: "t" }, t(titleKey)), el("span", { className: "s" }, t(textKey))));
  const diy = card("ch_diy_h", "ch_diy_p");
  diy.addEventListener("click", buildPlan);
  const help = card("ch_help_h", "ch_help_p");
  help.addEventListener("click", () => {
    handoverFrom = "choice";
    startPlanFetch();
    detailsScreen();
  });
  const list = el("div", { className: "options" }, diy, help);
  sideScreen(goBack, ask(t("ch_title")), list, el("p", { className: "hint", style: "margin-top:22px" }, t("ch_note")));
}

// ---- Hand the case over to Fraud Aid ---------------------------------------------------------

function helpBox() {
  const go = el("button", { className: "button", type: "button" }, t("help_btn"));
  go.addEventListener("click", () => {
    handoverFrom = "plan";
    detailsScreen();
  });
  return el("div", { className: "help" }, el("h3", {}, t("help_h")), el("p", {}, t("help_p")), el("div", { className: "row", style: "margin-top:18px" }, go));
}

function sideScreen(backFn, ...content) {
  reading(false);
  const top = el("div", { className: "top" });
  if (backFn) {
    const back = el("button", { className: "back", type: "button" }, t("back"));
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
  if (typeof body.detail === "string") return body.detail.includes("cannot take") ? t("err_not_eligible") : t("went_wrong");
  if (Array.isArray(body.detail) && body.detail[0]) return String(body.detail[0].msg || "").includes("IBAN") ? t("err_iban") : t("err_check");
  return t("went_wrong");
}

function detailsScreen() {
  view = detailsScreen;
  const [fName, name] = field("full_name", t("f_name"), { autocomplete: "name", required: true, maxLength: 100, value: contact.full_name || "" });
  const [fEmail, email] = field("email", t("f_email"), { type: "email", autocomplete: "email", required: true, value: contact.email || "" });
  const [fPhone, phone] = field("phone", t("f_phone"), { type: "tel", autocomplete: "tel", required: true, maxLength: 30, value: contact.phone || "" });
  const [fAddr, addr] = field("address", t("f_address"), { autocomplete: "street-address", required: true, maxLength: 200, placeholder: t("f_address_ph"), value: contact.address || "" });
  const [fIban, iban] = field("iban", t("f_iban"), { required: true, maxLength: 40, placeholder: "BE00 0000 0000 0000", value: contact.iban || "" });
  const keep = () => (contact = { full_name: name.value.trim(), email: email.value.trim(), phone: phone.value.trim(), address: addr.value.trim(), iban: iban.value.trim() });
  [name, email, phone, addr, iban].forEach((x) => x.addEventListener("input", keep));
  const form = el("form", {}, fName, fEmail, fPhone, fAddr, fIban, el("div", { className: "row" }, el("button", { className: "button", type: "submit" }, t("continue"))));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    keep();
    termsScreen();
  });
  sideScreen(handoverFrom === "plan" && lastPlan ? () => showPlan(lastPlan) : choiceScreen, ask(t("d_title")), el("p", { className: "sub", style: "margin-top:14px" }, t("d_sub")), form);
  name.focus();
}

async function termsScreen() {
  view = termsScreen;
  const tm = await fetch(`/api/terms?lang=${LANG}`).then((r) => r.json()).catch(() => null);
  if (!tm) return sideScreen(detailsScreen, ask(t("err_title")), el("p", { className: "sub" }, t("t_fail_sub")));
  const list = (items) => el("ul", {}, ...items.map((x) => el("li", {}, x)));
  const sec = (title, node) => el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, title), node);

  const sign = el("input", { className: "text", id: "signature", required: true, maxLength: 100, autocomplete: "off", placeholder: t("sign_ph") });
  const box = (name, text, required = true) => {
    const input = el("input", { type: "checkbox", name, required });
    return [el("label", { className: "consent" }, input, text), input];
  };
  const [cPrivacy, iPrivacy] = box("privacy", tm.privacy);
  const [cTerms, iTerms] = box("terms", t("c_terms"));
  const [cMandate, iMandate] = box("mandate", t("c_mandate"));
  const [cShare, iShare] = box("share", tm.share, false);
  const err = el("p", { className: "error", hidden: true, role: "alert" });
  const go = el("button", { className: "button", type: "submit" }, t("send_case"));

  const form = el(
    "form",
    {},
    el("p", { className: "urgent" }, tm.draft_notice),
    sec(t("t_costs"), list(tm.fee)),
    sec(t("t_wedo"), list(tm.we_do)),
    sec(t("t_youdo"), list(tm.you_do)),
    sec(t("t_rights"), list(tm.rights)),
    sec(t("t_auth"), el("p", { className: "mandate" }, tm.mandate)),
    el("div", { className: "field" }, el("label", { htmlFor: "signature" }, t("sign_label")), sign),
    el("div", { className: "checks" }, cPrivacy, cTerms, cMandate, cShare),
    err,
    el("div", { className: "row" }, go),
  );
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.hidden = true;
    go.disabled = true;
    go.textContent = t("sending");
    if (!lastPlan && planPromise) await planPromise;
    const body = {
      answers: { ...planBody(true), summary: undefined },
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
      go.textContent = t("send_case");
    }
  });
  sideScreen(detailsScreen, ask(t("t_title")), el("div", { style: "margin-top:24px" }, form));
}

function evidenceScreen() {
  view = evidenceScreen;
  const list = el("ul", { className: "uploads" });
  const pick = el("input", { type: "file", multiple: true, accept: ".pdf,.png,.jpg,.jpeg,.heic,.txt", id: "files", className: "text" });
  const err = el("p", { className: "error", hidden: true, role: "alert" });
  pick.addEventListener("change", async () => {
    err.hidden = true;
    for (const f of [...pick.files]) {
      const li = el("li", {}, `${f.name} `, el("span", { className: "quiet" }, t("uploading")));
      list.append(li);
      const fd = new FormData();
      fd.append("file", f);
      const r = await fetch(`/api/cases/${caseRef.id}/evidence`, { method: "POST", headers: { "X-Case-Token": caseRef.token }, body: fd }).catch(() => null);
      li.lastChild.textContent = r && r.ok ? t("added") : t("failed");
      if (!r || !r.ok) {
        err.textContent = r ? await errorText(r) : t("upload_fail");
        err.hidden = false;
      }
    }
    pick.value = "";
  });
  const done = el("button", { className: "button", type: "button" }, t("finish"));
  done.addEventListener("click", doneScreen);
  sideScreen(null, ask(t("e_title")), el("p", { className: "sub", style: "margin-top:14px" }, t("e_sub")), el("div", { className: "field" }, el("label", { htmlFor: "files" }, t("e_choose")), pick), list, err, el("div", { className: "row" }, done));
}

function doneScreen() {
  view = doneScreen;
  const link = `${location.origin}/status.html#${caseRef.id}.${caseRef.token}`;
  const copy = el("button", { className: "button ghost", type: "button" }, t("copy_link"));
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(link);
      copy.textContent = t("copied");
    } catch {
      copy.textContent = t("copy_select");
    }
  });
const firstSteps = el("button", { className: "button", type: "button" }, t("done_plan"));
  firstSteps.addEventListener("click", () => (lastPlan ? showPlan(lastPlan) : buildPlan()));
  sideScreen(null, ask(t("done_title")), el("p", { className: "ref" }, caseRef.id), el("p", { className: "sub" }, t("done_text", { email: contact.email })), el("p", { className: "linkbox" }, link), el("div", { className: "row" }, firstSteps, copy, el("a", { className: "button ghost", href: link }, t("open_case"))));
}

window.addEventListener("langchange", () => view && view());

start();
