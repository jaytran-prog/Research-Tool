#!/usr/bin/env python3
"""Validate a deck spec and render it as a web deck (HTML), PDF and/or editable PowerPoint.

Usage:
  python3 render_deck.py deck.json [--formats html,pdf,pptx] [--cut all|team|investor|client]
                                   [--theme default|path/to/theme.json] [--out DIR] [--check]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck_layout import EXHIBITS, build  # noqa: E402

LAYOUTS = {"cover", "exec_summary", "hero", "section", "standard", "full", "sources"}
CONTENT = {"standard", "full", "hero"}
LEVELS = {"strong", "mixed", "weak"}
NEEDS_SOURCES = {"bar", "dot_ci", "hero_stat"}
SHOULD_SOURCE = {"table", "matrix_2x2", "options"}
CUTS = {"team", "investor", "client"}
CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          "/Applications/Chromium.app/Contents/MacOS/Chromium", "google-chrome", "chromium", "chromium-browser"]


def validate(deck):
    errors, warnings = [], []
    source_ns = {s.get("n") for s in deck.get("sources", [])}
    ids = set()
    if not deck.get("slides"):
        errors.append("deck has no slides")
    for i, s in enumerate(deck.get("slides", []), 1):
        sid = s.get("id", f"#{i}")
        where = f"slide {sid}"
        if sid in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(sid)
        layout = s.get("layout", "standard")
        if layout not in LAYOUTS:
            errors.append(f"{where}: unknown layout '{layout}'")
            continue
        for c in s.get("cuts", []) or []:
            if c not in CUTS:
                errors.append(f"{where}: unknown cut '{c}'")
        for n in s.get("sources", []) or []:
            if n not in source_ns:
                errors.append(f"{where}: source [{n}] is not in the sources list")
        title = s.get("title", "")
        if layout in CONTENT | {"exec_summary"}:
            if not title:
                errors.append(f"{where}: missing title")
            elif len(title.split()) > 25:
                warnings.append(f"{where}: title is {len(title.split())} words (aim for ≤ 20)")
            if s.get("evidence") not in LEVELS:
                errors.append(f"{where}: evidence must be strong, mixed or weak")
        if layout in CONTENT:
            ex = s.get("exhibit") or {}
            kind = ex.get("kind")
            if kind not in EXHIBITS:
                errors.append(f"{where}: unknown exhibit kind '{kind}'")
                continue
            if layout == "hero" and kind != "hero_stat":
                errors.append(f"{where}: hero layout needs a hero_stat exhibit")
            if kind in NEEDS_SOURCES and not s.get("sources"):
                errors.append(f"{where}: {kind} shows data but cites no sources")
            if kind in SHOULD_SOURCE and not s.get("sources"):
                warnings.append(f"{where}: {kind} cites no sources — fine only if every cell is client-provided")
            if len(s.get("takeaways", []) or []) > 3:
                warnings.append(f"{where}: more than 3 takeaways")
            if len((s.get("so_what") or "").split()) > 25:
                warnings.append(f"{where}: so_what is over 25 words")
            errors += [f"{where}: {m}" for m in check_exhibit(kind, ex)]
        if layout == "exec_summary":
            if not 3 <= len(s.get("points", [])) <= 4:
                warnings.append(f"{where}: executive summary should have 3–4 points")
            if not s.get("recommendation"):
                errors.append(f"{where}: executive summary needs a recommendation")
    return errors, warnings


def check_exhibit(kind, ex):
    errs = []
    if kind == "bar":
        cats = ex.get("categories", [])
        for ser in ex.get("series", []):
            if len(ser.get("values", [])) != len(cats):
                errs.append("bar series length doesn't match categories")
        if len(cats) < 2:
            errs.append("bar needs at least 2 categories (data rule) — use bullets or a hero stat")
    elif kind == "dot_ci":
        for r in ex.get("rows", []):
            if not all(k in r for k in ("value", "low", "high")):
                errs.append(f"dot_ci row '{r.get('label')}' needs value, low and high")
            elif not r["low"] <= r["value"] <= r["high"]:
                errs.append(f"dot_ci row '{r.get('label')}': value must lie between low and high")
    elif kind == "matrix_2x2":
        if not ex.get("basis"):
            errs.append("matrix_2x2 needs a 'basis' saying how positions were judged (data rule)")
        for p in ex.get("points", []):
            if not (0 <= float(p.get("x", -1)) <= 1 and 0 <= float(p.get("y", -1)) <= 1):
                errs.append(f"matrix point '{p.get('label')}' needs x and y between 0 and 1")
    elif kind == "options":
        n = len(ex.get("criteria", []))
        for o in ex.get("options", []):
            sc = o.get("scores", [])
            if len(sc) != n or any(not 0 <= v <= 4 for v in sc):
                errs.append(f"option '{o.get('name')}' needs {n} scores between 0 and 4")
    elif kind == "roadmap":
        for lane in ex.get("lanes", []):
            for b in lane.get("bars", []):
                if b.get("start", 0) > b.get("end", 0):
                    errs.append(f"roadmap bar '{b.get('label')}' ends before it starts")
    elif kind == "table":
        n = len(ex.get("columns", []))
        if any(len(r) != n for r in ex.get("rows", [])):
            errs.append("table rows must have one cell per column")
    return errs


def load_theme(arg):
    here = os.path.dirname(os.path.abspath(__file__))
    path = arg if arg.endswith(".json") else os.path.join(here, "themes", f"{arg}.json")
    with open(path, encoding="utf-8") as f:
        theme = json.load(f)
    if not arg.endswith("default.json") and arg != "default":
        with open(os.path.join(here, "themes", "default.json"), encoding="utf-8") as f:
            base = json.load(f)
        base["colors"].update(theme.get("colors", {}))
        base["fonts"].update(theme.get("fonts", {}))
        theme = base
    return theme


def apply_cut(deck, cut):
    if cut in (None, "all"):
        return deck
    d = dict(deck)
    d["slides"] = [s for s in deck["slides"] if not s.get("cuts") or cut in s["cuts"]]
    return d


def find_chrome():
    for c in CHROME:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        if not os.path.isabs(c) and shutil.which(c):
            return shutil.which(c)
    return None


def html_to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if not chrome:
        return False
    with tempfile.TemporaryDirectory() as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={profile}",
               "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
               f"--print-to-pdf={pdf_path}", "file://" + os.path.abspath(html_path)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return os.path.exists(pdf_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--formats", default="html,pdf,pptx")
    ap.add_argument("--cut", default="all", choices=["all", "team", "investor", "client"])
    ap.add_argument("--theme", default="default")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true", help="validate only")
    args = ap.parse_args()

    with open(args.deck, encoding="utf-8") as f:
        deck = json.load(f)
    errors, warnings = validate(deck)
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        sys.exit(f"{len(errors)} error(s) — fix deck.json and run again")
    if args.check:
        print(f"OK: {len(deck['slides'])} slides valid")
        return

    theme = load_theme(args.theme)
    deck = apply_cut(deck, args.cut)
    built = build(deck)
    out_dir = args.out or os.path.dirname(os.path.abspath(args.deck))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.deck))[0] + ("" if args.cut == "all" else f"-{args.cut}")
    formats = [x.strip() for x in args.formats.split(",") if x.strip()]
    written = []

    html_path = os.path.join(out_dir, stem + ".html")
    if "html" in formats or "pdf" in formats:
        from render_html import render_html
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(render_html(built, deck, theme))
        if "html" in formats:
            written.append(html_path)
    if "pdf" in formats:
        pdf_path = os.path.join(out_dir, stem + ".pdf")
        if html_to_pdf(html_path, pdf_path):
            written.append(pdf_path)
        else:
            print("WARNING: no Chrome/Chromium found — open the HTML and print to PDF instead")
        if "html" not in formats:
            os.remove(html_path)
    if "pptx" in formats:
        try:
            from render_pptx import render_pptx
        except ImportError:
            print("WARNING: python-pptx is not installed — run: pip install python-pptx")
        else:
            pptx_path = os.path.join(out_dir, stem + ".pptx")
            render_pptx(built, deck, theme, pptx_path)
            written.append(pptx_path)
    print(f"Rendered {len(built)} slides ({args.cut}):")
    for w in written:
        print("  " + w)


if __name__ == "__main__":
    main()
