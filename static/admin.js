const app = document.getElementById("app");
let token = sessionStorage.getItem("fa_admin") || "";

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  Object.assign(n, props);
  n.append(...kids);
  return n;
}
const api = (path, opts = {}) => fetch(path, { ...opts, headers: { "X-Admin-Token": token, "Content-Type": "application/json", ...(opts.headers || {}) } });
const when = (iso) => new Date(iso).toLocaleString("en-BE", { dateStyle: "medium", timeStyle: "short" });
const eur = (n) => (n == null ? "unknown" : new Intl.NumberFormat("en-BE", { style: "currency", currency: "EUR", minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n));

function login(msg = "") {
  const input = el("input", { className: "text", type: "password", placeholder: "Admin token", ariaLabel: "Admin token", autocomplete: "off" });
  const form = el("form", {}, input, el("p", { className: "error", hidden: !msg, role: "alert" }, msg), el("div", { className: "row" }, el("button", { className: "button", type: "submit" }, "Open")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    token = input.value;
    sessionStorage.setItem("fa_admin", token);
    list();
  });
  app.replaceChildren(el("section", { className: "screen" }, el("h2", { className: "big" }, "Back office"), el("div", { style: "margin-top:24px;max-width:24rem" }, form)));
  input.focus();
}

async function list() {
  const r = await api("/api/admin/cases").catch(() => null);
  if (!r) return login("Could not reach the server.");
  if (r.status === 403) return login((await r.json()).detail);
  const rows = await r.json();
  const table = el("table", {}, el("thead", {}, el("tr", {}, ...["Reference", "Received", "Name", "Bank", "Amount", "Verdict", "Files", "Status"].map((h) => el("th", {}, h)))));
  const body = el("tbody");
  rows.forEach((c) => {
    const tr = el("tr", { className: "row-link", tabIndex: 0 }, ...[c.id, when(c.created_at), c.full_name, c.bank, eur(c.amount), c.level, String(c.files), c.status].map((v) => el("td", {}, v)));
    tr.addEventListener("click", () => detail(c.id));
    tr.addEventListener("keydown", (e) => e.key === "Enter" && detail(c.id));
    body.append(tr);
  });
  table.append(body);
  app.replaceChildren(el("section", { className: "screen" }, el("h2", { className: "big" }, `${rows.length} case${rows.length === 1 ? "" : "s"}`), rows.length ? el("div", { style: "margin-top:28px" }, table) : el("p", { className: "sub", style: "margin-top:14px" }, "No cases yet.")));
}

async function download(caseId, f) {
  const r = await api(`/api/admin/cases/${caseId}/evidence/${f.id}`);
  const url = URL.createObjectURL(await r.blob());
  const a = el("a", { href: url, download: f.original_name });
  a.click();
  URL.revokeObjectURL(url);
}

async function detail(id) {
  const r = await api(`/api/admin/cases/${encodeURIComponent(id)}`);
  if (!r.ok) return list();
  const c = await r.json();
  const kv = (pairs) => {
    const dl = el("dl");
    pairs.forEach(([k, v]) => dl.append(el("dt", {}, k), el("dd", {}, String(v ?? ""))));
    return dl;
  };
  const a = c.answers;
  const back = el("button", { className: "back", type: "button" }, "← All cases");
  back.addEventListener("click", list);

  const select = el("select", { ariaLabel: "Status" }, ...c.statuses.map((s) => el("option", { value: s, selected: s === c.status }, s)));
  const note = el("input", { className: "text", maxLength: 300, placeholder: "Update shown to the victim (optional)", ariaLabel: "Update note" });
  const save = el("button", { className: "button", type: "button" }, "Update status");
  save.addEventListener("click", async () => {
    await api(`/api/admin/cases/${id}/status`, { method: "POST", body: JSON.stringify({ status: select.value, note: note.value }) });
    detail(id);
  });

  const docs = c.docs.map((d) => {
    const copy = el("button", { type: "button" }, "Copy");
    copy.addEventListener("click", () => navigator.clipboard.writeText(d.text).then(() => (copy.textContent = "Copied")));
    return el("div", { className: "doc" }, el("header", {}, el("span", { className: "label" }, d.title), copy), el("pre", {}, d.text));
  });

  const files = el("ul", { className: "uploads" });
  if (!c.files.length) files.append(el("li", { className: "quiet" }, "No files."));
  c.files.forEach((f) => {
    const b = el("button", { className: "back", type: "button" }, f.original_name);
    b.addEventListener("click", () => download(id, f));
    files.append(el("li", {}, b, ` ${Math.max(1, Math.round(f.size / 1024))} KB`));
  });

  const events = el("ol", { className: "timeline" });
  [...c.events].reverse().forEach((e) => events.append(el("li", {}, el("span", { className: "label quiet" }, `${when(e.at)} ${e.public ? "" : "(internal)"}`), el("span", {}, e.note.startsWith("status:") ? "Status: " + e.note.slice(7) : e.note))));

  app.replaceChildren(
    el(
      "section",
      { className: "screen" },
      el("div", { className: "top" }, back),
      el("h2", { className: "big", style: "margin-top:18px" }, c.id),
      el("div", { className: "cols", style: "margin-top:28px" },
        el("div", {}, el("p", { className: "label quiet" }, "Client"), kv([["Name", c.full_name], ["Email", c.email], ["Phone", c.phone], ["Address", c.address], ["IBAN", c.iban], ["Signed", c.mandate_signature], ["Terms", c.terms_version], ["Share intel", c.share_intel ? "yes, without name" : "no"]])),
        el("div", {}, el("p", { className: "label quiet" }, "Case"), kv([["Verdict", c.level], ["Amount", eur(a.amount_eur)], ["Bank", a.bank], ["How", a.how], ["Pretended", a.impersonated], ["Approved", a.authorised], ["Paid by", a.method], ["When", a.when], ["Codes shared", a.shared_credentials], ["Remote access", a.remote_access], ["Told bank", a.told_bank], ["Told police", a.told_police], ["Scammer", a.scammer_details]])),
      ),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Statement"), el("p", { style: "font-size:0.95rem" }, c.summary)),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Status"), el("div", { className: "row", style: "margin-top:8px" }, select, note, save)),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Claim pack"), ...docs),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Evidence"), files),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "History"), events),
    ),
  );
}

token ? list() : login();
