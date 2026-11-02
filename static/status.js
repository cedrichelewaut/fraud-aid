const app = document.getElementById("app");
document.body.classList.add("reading");
const [id, token] = location.hash.slice(1).split(".");
let view = null; // how to draw the current state again, for when the language changes

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  Object.assign(n, props);
  n.append(...kids);
  return n;
}

const locale = () => ({ en: "en-BE", fr: "fr-BE", nl: "nl-BE" })[LANG];
const when = (iso) => new Date(iso).toLocaleString(locale(), { dateStyle: "medium", timeStyle: "short" });
const H = { "X-Case-Token": token || "" };

async function load() {
  if (!id || !token) return message("s_incomplete", "s_incomplete_sub");
  const r = await fetch(`/api/cases/${encodeURIComponent(id)}`, { headers: H }).catch(() => null);
  if (!r) return message("err_title", "s_err_sub");
  if (r.status === 404) return message("s_nf", "s_nf_sub");
  if (r.status === 403) return message("s_bad", "s_bad_sub");
  render(await r.json());
}

function message(titleKey, subKey) {
  view = () => message(titleKey, subKey);
  app.replaceChildren(el("section", { className: "screen" }, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big" }, t(titleKey)), el("p", { className: "sub" }, t(subKey)))));
}

// System updates are stored as a kind and a code, so each person reads them in their own language.
function eventText(e) {
  if (e.kind === "created") return t("ev_created");
  if (e.kind === "evidence") return t("ev_file", { name: e.note.replace(/^File added: /, "") });
  if (e.note.startsWith("status:")) return t("st_" + e.note.slice(7));
  return e.note; // a note written by the team, shown as written
}

function render(c) {
  view = () => render(c);
  const events = el("ol", { className: "timeline" });
  [...c.events].reverse().forEach((e) => events.append(el("li", {}, el("span", { className: "label quiet" }, when(e.at)), el("span", {}, eventText(e)))));

  const files = el("ul", { className: "uploads" });
  if (!c.files.length) files.append(el("li", { className: "quiet" }, t("s_nofiles")));
  c.files.forEach((f) => files.append(el("li", {}, `${f.original_name} `, el("span", { className: "quiet" }, `${Math.max(1, Math.round(f.size / 1024))} KB`))));

  const err = el("p", { className: "error", hidden: true, role: "alert" });
  const pick = el("input", { type: "file", multiple: true, accept: ".pdf,.png,.jpg,.jpeg,.heic,.txt", id: "more", className: "text" });
  pick.addEventListener("change", async () => {
    err.hidden = true;
    for (const f of [...pick.files]) {
      const fd = new FormData();
      fd.append("file", f);
      const r = await fetch(`/api/cases/${encodeURIComponent(id)}/evidence`, { method: "POST", headers: H, body: fd }).catch(() => null);
      if (!r || !r.ok) {
        err.textContent = t("upload_fail");
        err.hidden = false;
      }
    }
    load();
  });

  const del = el("button", { className: "button ghost", type: "button" }, t("s_delete"));
  del.addEventListener("click", async () => {
    if (!confirm(t("s_confirm"))) return;
    const r = await fetch(`/api/cases/${encodeURIComponent(id)}`, { method: "DELETE", headers: H }).catch(() => null);
    if (r && r.ok) message("s_deleted", "s_deleted_sub");
    else {
      err.textContent = t("s_delete_fail");
      err.hidden = false;
    }
  });

  app.replaceChildren(
    el(
      "section",
      { className: "screen" },
      el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("p", { className: "label quiet" }, t("s_ref", { id: c.id })), el("h2", { className: "big", tabIndex: -1 }, t("st_" + c.status))),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, t("s_updates")), events),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, t("s_files")), files, el("div", { className: "field" }, el("label", { htmlFor: "more" }, t("s_addmore")), pick)),
      err,
      el("div", { className: "row", style: "margin-top:44px" }, del),
    ),
  );
}

window.addEventListener("langchange", () => view && view());
load();
