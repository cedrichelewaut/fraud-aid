"""Builds the static demo: the app's front end plus the Python backend packaged for Pyodide.

    python3 demo/build_demo.py --pyodide /path/to/pyodide --out /path/to/site/public/fraud-aid-demo

Pyodide (https://pyodide.org, MPL-2.0) is copied from a release download; only the files the demo needs.
"""

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKGS = ["pydantic", "pydantic_core", "annotated_types", "typing_extensions", "sqlite3"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pyodide", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    py, out = Path(args.pyodide), Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # Front end: copy and make every path relative so it works under any folder.
    for f in (ROOT / "static").iterdir():
        if f.is_dir():
            shutil.copytree(f, out / f.name)
        elif f.suffix == ".css":
            (out / f.name).write_text(f.read_text().replace('url("/fonts/', 'url("fonts/'))
        elif f.suffix in {".html", ".js"}:
            t = f.read_text()
            t = re.sub(r'(href|src)="/(?!/)', r'\1="', t)
            t = t.replace('href=""', 'href="./"')
            t = t.replace('"/logo.svg"', '"logo.svg"')
            t = t.replace("`${location.origin}/status.html#", "`${location.origin}${location.pathname.replace(/[^/]*$/, '')}status.html#")
            if f.suffix == ".html":
                t = t.replace("</head>", '  <script src="demo.js"></script>\n</head>')
                t = t.replace("<head>", '<head>\n  <meta name="robots" content="noindex">', 1) if "noindex" not in t else t
            (out / f.name).write_text(t)
        else:
            shutil.copy(f, out / f.name)
    shutil.copy(ROOT / "demo" / "demo.js", out / "demo.js")

    # Backend: app package plus the browser adapter, zipped for Pyodide.
    with zipfile.ZipFile(out / "app.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in (ROOT / "app").glob("*.py"):
            z.write(f, f"app/{f.name}")
        z.write(ROOT / "demo" / "demo_api.py", "demo_api.py")

    # Pyodide: the runtime and only the packages needed.
    pout = out / "pyodide"
    pout.mkdir()
    for name in ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip"]:
        shutil.copy(py / name, pout / name)
    lock = json.loads((py / "pyodide-lock.json").read_text())
    keep = {}
    for k, v in lock["packages"].items():
        if k.replace("-", "_") in PKGS:
            keep[k] = v
            shutil.copy(py / v["file_name"], pout / v["file_name"])
    lock["packages"] = keep
    (pout / "pyodide-lock.json").write_text(json.dumps(lock))
    shutil.copy(py / "pyodide.js", pout / "pyodide.js")
    print("built", out, sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) // 1024, "KB")


if __name__ == "__main__":
    main()
