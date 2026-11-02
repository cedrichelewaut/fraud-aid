const app = document.getElementById("app");
const [id, token] = location.hash.slice(1).split(".");

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  Object.assign(n, props);
  n.append(...kids);
  return n;
}

const when = (iso) => new Date(iso).toLocaleString("en-BE", { dateStyle: "medium", timeStyle: "short" });
const H = { "X-Case-Token": token || "" };

async function load() {
  if (!id || !token) return message("This link is incomplete.", "Use the full link we gave you when you sent your case.");
  const r = await fetch(`/api/cases/${encodeURIComponent(id)}`, { headers: H }).catch(() => null);
  if (!r) return message("Something went wrong.", "Please try again in a moment.");
  if (r.status === 404) return message("Case not found.", "It may have been deleted.");
  if (r.status === 403) return message("This link is not valid.", "Check that you copied the whole link.");
  render(await r.json());
}

function message(title, text) {
  app.replaceChildren(el("section", { className: "screen" }, el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("h2", { className: "big" }, title), el("p", { className: "sub" }, text))));
}

function render(c) {
  const events = el("ol", { className: "timeline" });
  [...c.events].reverse().forEach((e) => events.append(el("li", {}, el("span", { className: "label quiet" }, when(e.at)), el("span", {}, e.note))));

  const files = el("ul", { className: "uploads" });
  if (!c.files.length) files.append(el("li", { className: "quiet" }, "No files yet."));
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
        const b = r ? await r.json().catch(() => ({})) : {};
        err.textContent = b.detail || "Upload failed.";
        err.hidden = false;
      }
    }
    load();
  });

  const del = el("button", { className: "button ghost", type: "button" }, "Delete my case and all my files");
  del.addEventListener("click", async () => {
    if (!confirm("This permanently deletes your case, your details and all your files. Continue?")) return;
    const r = await fetch(`/api/cases/${encodeURIComponent(id)}`, { method: "DELETE", headers: H }).catch(() => null);
    if (r && r.ok) message("Your case has been deleted.", "We removed your details, your answers and your files.");
    else err.textContent = "Deleting failed. Please try again.", (err.hidden = false);
  });

  app.replaceChildren(
    el(
      "section",
      { className: "screen" },
      el("div", { className: "ask" }, el("img", { src: "/logo.svg", alt: "", width: 44, height: 44 }), el("p", { className: "label quiet" }, `Reference ${c.id}`), el("h2", { className: "big", tabIndex: -1 }, c.status_label)),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Updates"), events),
      el("div", { className: "terms-sec" }, el("p", { className: "label quiet" }, "Your files"), files, el("div", { className: "field" }, el("label", { htmlFor: "more" }, "Add more files"), pick)),
      err,
      el("div", { className: "row", style: "margin-top:44px" }, del),
    ),
  );
}

load();
