// Demo mode: the real Fraud Aid rules run in the browser (Python via Pyodide). Nothing is sent to a server.
// This file replaces fetch() for /api/* and shows a banner. Cases are kept in this browser only (IndexedDB).
(function () {
  const BASE = new URL(".", document.currentScript.src).href;
  const realFetch = window.fetch.bind(window);
  let ready = null;
  let py = null;
  let pyodide = null;

  function load() {
    if (ready) return ready;
    ready = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = BASE + "pyodide/pyodide.js";
      s.onload = resolve;
      s.onerror = () => reject(new Error("Could not load the demo engine."));
      document.head.append(s);
    })
      .then(() => loadPyodide({ indexURL: BASE + "pyodide/" }))
      .then(async (p) => {
        pyodide = p;
        await p.loadPackage(["pydantic", "sqlite3"]);
        p.FS.mkdirTree("/data");
        p.FS.mount(p.FS.filesystems.IDBFS, {}, "/data");
        await new Promise((res, rej) => p.FS.syncfs(true, (e) => (e ? rej(e) : res())));
        const zip = await (await realFetch(BASE + "app.zip")).arrayBuffer();
        p.unpackArchive(zip, "zip", { extractDir: "/srv" });
        await p.runPythonAsync("import sys; sys.path.insert(0, '/srv')\nimport demo_api");
        py = p.pyimport("demo_api");
      });
    return ready;
  }

  const persist = () => new Promise((res) => pyodide.FS.syncfs(false, () => res()));

  async function call(method, url, init) {
    await load();
    const u = new URL(url, location.href);
    const query = Object.fromEntries(u.searchParams);
    const headers = {};
    const h = init.headers || {};
    (h instanceof Headers ? [...h.entries()] : Object.entries(h)).forEach(([k, v]) => (headers[k] = v));
    let body = null, fname = "", ftype = "", fbytes = null;
    if (init.body instanceof FormData) {
      const f = init.body.get("file");
      fname = f.name; ftype = f.type; fbytes = new Uint8Array(await f.arrayBuffer());
    } else if (typeof init.body === "string") {
      body = init.body;
    }
    const res = await py.handle(method, u.pathname.replace(/^.*?\/api\//, "/api/"), JSON.stringify(query), JSON.stringify(headers), body, fname, ftype, fbytes);
    const [status, text] = res.toJs();
    res.destroy?.();
    if (method !== "GET") await persist();
    const parsed = JSON.parse(text);
    if (status === 200 && parsed && parsed.__file__) {
      const bytes = pyodide.FS.readFile(parsed.__file__);
      return new Response(bytes, { status: 200, headers: { "Content-Type": parsed.type } });
    }
    return new Response(text, { status, headers: { "Content-Type": "application/json" } });
  }

  window.fetch = function (input, init = {}) {
    const url = typeof input === "string" ? input : input.url;
    const path = new URL(url, location.href).pathname;
    if (/(^|\/)api\//.test(path)) return call((init.method || "GET").toUpperCase(), url, init);
    return realFetch(input, init);
  };

  // Start loading the engine right away so the first answer is quick.
  load().catch((e) => console.error(e));

  // Banner
  const bar = document.createElement("div");
  bar.setAttribute("role", "note");
  bar.style.cssText = "background:#111;color:#fff;font:14px/1.4 Aileron,system-ui,sans-serif;padding:9px 16px;text-align:center;position:relative;z-index:50";
  const admin = /admin\.html$/.test(location.pathname) ? " Back office token: <b>demo</b>." : "";
  bar.innerHTML = 'Demo: it runs entirely in your browser and sends nothing anywhere. Please do not enter real personal data. Cases are saved on this device only.' + admin + ' <a href="https://github.com/cedrichelewaut/fraud-aid" style="color:#fff">Code</a>';
  document.addEventListener("DOMContentLoaded", () => document.body.prepend(bar));
})();
