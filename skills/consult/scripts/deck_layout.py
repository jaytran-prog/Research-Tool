"""Layout engine: turns a deck spec into drawing primitives shared by the HTML and PowerPoint backends.

Coordinates are pixels on a 1280x720 slide (96 dpi, so 13.333 x 7.5 inches).
Colours are theme keys (e.g. "accent") or literal "#RRGGBB" values.
"""
import math

W, H = 1280, 720
MX = 64
CONTENT_W = W - 2 * MX
TITLE_Y = 56
RULE_Y = 150
BODY_Y = 170
SOWHAT_Y, SOWHAT_H = 626, 44
FOOT_Y = 682
RAIL_X, RAIL_W = 856, 360
EXHIBIT_W_WITH_RAIL = RAIL_X - MX - 32

EVIDENCE_LABEL = {"strong": "Strong evidence", "mixed": "Mixed evidence", "weak": "Weak evidence"}
STATUS_COLOR = {"supported": "strong", "rejected": "weak", "open": "mixed",
                "known": "ink", "assumed": "mixed", "unknown": "weak"}


# ---------- text measurement (approximate; good enough for layout) ----------

def text_lines(text, size, width, char_w=0.52):
    cpl = max(1, int(width / (size * char_w)))
    total = 0
    for para in str(text).split("\n"):
        words = para.split()
        if not words:
            total += 1
            continue
        lines, cur = 1, 0
        for word in words:
            n = len(word)
            if cur == 0:
                cur = n
            elif cur + 1 + n <= cpl:
                cur += 1 + n
            else:
                lines += 1
                cur = n
        total += lines
    return total


def text_height(text, size, width, lh=1.3, char_w=0.52):
    return text_lines(text, size, width, char_w) * size * lh


def fit_size(text, width, max_lines, sizes, char_w=0.52):
    for size in sizes:
        if text_lines(text, size, width, char_w) <= max_lines:
            return size
    return sizes[-1]


def truncate(text, limit):
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


# ---------- primitives ----------

def T(x, y, w, h, text="", size=14, color="ink", bold=False, font="body", align="left",
      valign="top", italic=False, runs=None, lh=1.25):
    """Text box. `runs` is a list of dicts {text, bold, color, size, italic} that replaces `text`."""
    if runs is None:
        runs = [{"text": str(text)}]
    return {"type": "text", "x": x, "y": y, "w": w, "h": h, "runs": runs, "size": size, "color": color,
            "bold": bold, "font": font, "align": align, "valign": valign, "italic": italic, "lh": lh}


def R(x, y, w, h, fill=None, line=None, line_w=1, radius=0, hatch=False):
    return {"type": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill, "line": line,
            "line_w": line_w, "radius": radius, "hatch": hatch}


def E(x, y, w, h, fill=None, line=None, line_w=1):
    return {"type": "ellipse", "x": x, "y": y, "w": w, "h": h, "fill": fill, "line": line, "line_w": line_w}


def L(x1, y1, x2, y2, color="grey", w=1, dash=False):
    return {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "w": w, "dash": dash}


def DIAMOND(x, y, w, h, fill):
    return {"type": "diamond", "x": x, "y": y, "w": w, "h": h, "fill": fill}


def HARVEY(x, y, d, score):
    return {"type": "harvey", "x": x, "y": y, "d": d, "score": max(0, min(4, int(score)))}


def TABLE(x, y, col_w, row_h, rows, size, fills=None, header=True):
    """rows: list of lists of cells; a cell is a string or {text, color, bold}."""
    return {"type": "table", "x": x, "y": y, "w": sum(col_w), "h": sum(row_h), "col_w": col_w,
            "row_h": row_h, "rows": rows, "size": size, "fills": fills or [None] * len(rows), "header": header}


def BAR(x, y, w, h, spec):
    """A bar chart. The HTML backend draws it with bar_prims(); PowerPoint uses a native chart."""
    return {"type": "bar", "x": x, "y": y, "w": w, "h": h, "spec": spec}


# ---------- shared pieces ----------

def cell_text(cell):
    return cell.get("text", "") if isinstance(cell, dict) else str(cell)


def fmt_value(v, spec, default="{:,.1f}"):
    fmt = spec.get("value_format")
    if not fmt:
        fmt = "{:,.0f}" if float(v).is_integer() else default
    s = fmt.format(v).replace("-", "−")
    unit = spec.get("unit")
    if not unit or s.rstrip().endswith(unit):
        return s
    return f"{s}{unit}" if unit == "%" else f"{s} {unit}"


def evidence_badge(x, y, level, size=10):
    if level not in EVIDENCE_LABEL:
        return []
    return [E(x, y + 2, 9, 9, fill=level),
            T(x + 14, y - 1, 150, 14, EVIDENCE_LABEL[level], size=size, color="grey", bold=True)]


def header(slide):
    prims = []
    if slide.get("section"):
        prims.append(T(MX, 28, 900, 16, slide["section"].upper(), size=11, color="accent", bold=True))
    title = slide.get("title", "")
    size = fit_size(title, CONTENT_W, 2, [30, 27, 24], char_w=0.5)
    prims.append(T(MX, TITLE_Y, CONTENT_W, 116, title, size=size, color="ink", font="head", lh=1.2))
    prims.append(L(MX, RULE_Y, W - MX, RULE_Y, color="grey_light", w=1))
    return prims


def footer(slide, deck, page):
    prims = []
    by_n = {s.get("n"): s for s in deck.get("sources", [])}
    nums = [n for n in slide.get("sources") or [] if n in by_n]
    if nums:
        txt = "Sources: " + "; ".join(f"[{n}] {by_n[n].get('label', '')}" for n in nums)
        prims.append(T(MX, FOOT_Y, 900, 28, truncate(txt, 330), size=10, color="grey", lh=1.2))
    prims += evidence_badge(W - MX - 190, FOOT_Y, slide.get("evidence"))
    prims.append(T(W - MX - 40, FOOT_Y, 40, 14, str(page), size=10, color="grey", align="right"))
    return prims


def so_what_bar(text):
    return [R(MX, SOWHAT_Y, CONTENT_W, SOWHAT_H, fill="accent_soft"),
            R(MX, SOWHAT_Y, 5, SOWHAT_H, fill="accent"),
            T(MX + 22, SOWHAT_Y, CONTENT_W - 40, SOWHAT_H, size=15, valign="middle",
              runs=[{"text": "So what  ", "bold": True, "color": "accent"}, {"text": text}])]


def takeaways_rail(items, y0, bottom):
    prims = [T(RAIL_X, y0, RAIL_W, 16, "KEY TAKEAWAYS", size=11, color="accent", bold=True)]
    y = y0 + 30
    for item in items[:3]:
        h = text_height(item, 17, RAIL_W - 20, lh=1.3)
        if y + h > bottom:
            break
        prims.append(R(RAIL_X, y + 2, 4, h - 4, fill="accent"))
        prims.append(T(RAIL_X + 18, y, RAIL_W - 18, h, item, size=17, lh=1.3))
        y += h + 22
    return prims


# ---------- exhibits ----------

def bar_prims(x, y, w, h, spec):
    cats = spec.get("categories", [])
    series = spec.get("series", [])
    n, s = len(cats), max(1, len(series))
    highlight = set(spec.get("highlight", []))
    vals = [v for ser in series for v in ser.get("values", []) if v is not None]
    if not cats or not vals:
        return [T(x, y, w, 40, "No data", color="grey")]
    # All-negative data (e.g. weight change) is drawn as magnitudes with signed labels, so bars read left to right.
    mirror = max(vals) <= 0
    if mirror:
        vals = [abs(v) for v in vals]
    vmin, vmax = min(0, min(vals)), max(0, max(vals))
    span = (vmax - vmin) or 1
    palette = ["accent", "ink", "grey", "grey_light"]
    prims = []
    if s > 1:
        lx = x
        for j, ser in enumerate(series):
            prims.append(R(lx, y, 12, 12, fill=palette[j % 4]))
            prims.append(T(lx + 18, y - 2, 180, 16, ser.get("name", ""), size=12, color="grey"))
            lx += 200
        y, h = y + 28, h - 28

    def color_for(i, j):
        if s == 1:
            return "accent" if (i in highlight or not highlight) else "grey_bar"
        return palette[j % 4]

    if spec.get("orientation", "horizontal") == "horizontal":
        label_w = min(w * 0.32, 260)
        neg_pad = 110 if vmin < 0 else 0
        plot_x = x + label_w + 14 + neg_pad
        plot_w = w - label_w - 14 - neg_pad - 110
        zero_x = plot_x + (0 - vmin) / span * plot_w
        row_h = h / n
        bar_h = min(52, row_h * 0.62 / s)
        for i, cat in enumerate(cats):
            cy = y + i * row_h + row_h / 2
            prims.append(T(x, cy - row_h / 2, label_w, row_h, cat, size=15, align="right", valign="middle",
                           bold=i in highlight))
            for j, ser in enumerate(series):
                raw = ser["values"][i]
                if raw is None:
                    continue
                v = abs(raw) if mirror else raw
                est = (ser.get("estimate") or [False] * n)[i]
                by = cy - s * bar_h / 2 + j * bar_h
                left = plot_x + (min(0, v) - vmin) / span * plot_w
                bw = max(abs(v) / span * plot_w, 2)
                prims.append(R(left, by + 2, bw, bar_h - 4, fill=color_for(i, j), hatch=est))
                label = fmt_value(raw, spec) + (" est." if est else "")
                if v >= 0:
                    prims.append(T(left + bw + 8, by, 110, bar_h, label, size=14, valign="middle", bold=i in highlight))
                else:
                    prims.append(T(left - 118, by, 110, bar_h, label, size=14, valign="middle", align="right",
                                   bold=i in highlight))
        if vmin < 0:
            prims.append(L(zero_x, y, zero_x, y + h, color="grey", w=1))
    else:
        label_h = 44
        plot_y, plot_h = y + 24, h - 24 - label_h
        zero_y = plot_y + (vmax - 0) / span * plot_h
        col_w = w / n
        bar_w = min(90, col_w * 0.6 / s)
        for i, cat in enumerate(cats):
            cx = x + i * col_w + col_w / 2
            prims.append(T(cx - col_w / 2, plot_y + plot_h + 8, col_w, label_h, cat, size=14, align="center",
                           bold=i in highlight))
            for j, ser in enumerate(series):
                raw = ser["values"][i]
                if raw is None:
                    continue
                v = abs(raw) if mirror else raw
                est = (ser.get("estimate") or [False] * n)[i]
                bx = cx - s * bar_w / 2 + j * bar_w
                top = plot_y + (vmax - max(0, v)) / span * plot_h
                bh = max(abs(v) / span * plot_h, 2)
                prims.append(R(bx + 3, top, bar_w - 6, bh, fill=color_for(i, j), hatch=est))
                label = fmt_value(raw, spec) + (" est." if est else "")
                ly = top - 22 if v >= 0 else top + bh + 4
                prims.append(T(bx - 30, ly, bar_w + 60, 18, label, size=13, align="center", bold=i in highlight))
        prims.append(L(x, zero_y, x + w, zero_y, color="grey", w=1))
    return prims


def ex_bar(x, y, w, h, ex):
    return [BAR(x, y, w, h, ex)]


def ex_dot_ci(x, y, w, h, ex):
    rows = ex.get("rows", [])
    if not rows:
        return []
    highlight = set(ex.get("highlight", []))
    zero = ex.get("zero", 0)
    fmt = ex.get("value_format", "{:+.2f}")
    label_w = w * 0.34
    val_w = 170
    plot_x = x + label_w + 16
    plot_w = w - label_w - 16 - val_w - 10
    lo = min(min(r["low"] for r in rows), zero)
    hi = max(max(r["high"] for r in rows), zero)
    pad = (hi - lo) * 0.08 or 1
    lo, hi = lo - pad, hi + pad

    def X(v):
        return plot_x + (v - lo) / (hi - lo) * plot_w

    row_h = min(72, (h - 46) / len(rows))
    prims = [L(X(zero), y, X(zero), y + row_h * len(rows), color="grey", w=1, dash=True)]
    for i, r in enumerate(rows):
        cy = y + i * row_h + row_h / 2
        hl = i in highlight
        col = "accent" if hl else "ink"
        if i % 2 == 0:
            prims.append(R(x, cy - row_h / 2, w, row_h, fill="bg_soft"))
        runs = [{"text": r.get("label", ""), "bold": hl}]
        if r.get("note"):
            runs.append({"text": "\n" + r["note"], "color": "grey", "size": 11})
        prims.append(T(x + 8, cy - row_h / 2, label_w - 8, row_h, size=14, valign="middle", runs=runs, lh=1.2))
        prims.append(L(X(r["low"]), cy, X(r["high"]), cy, color=col, w=3))
        prims.append(L(X(r["low"]), cy - 7, X(r["low"]), cy + 7, color=col, w=2))
        prims.append(L(X(r["high"]), cy - 7, X(r["high"]), cy + 7, color=col, w=2))
        prims.append(E(X(r["value"]) - 8, cy - 8, 16, 16, fill=col))
        txt = f"{fmt.format(r['value'])} ({fmt.format(r['low'])} to {fmt.format(r['high'])})".replace("-", "−")
        prims.append(T(plot_x + plot_w + 14, cy - 12, val_w, 24, txt, size=13, valign="middle", bold=hl))
    by = y + row_h * len(rows) + 10
    if ex.get("left_label"):
        prims.append(T(plot_x, by, X(zero) - plot_x - 8, 30, "← " + ex["left_label"], size=12, color="grey",
                       align="right"))
    if ex.get("right_label"):
        prims.append(T(X(zero) + 8, by, max(plot_x + plot_w - X(zero), 260), 30, ex["right_label"] + " →", size=12,
                       color="grey"))
    if ex.get("unit"):
        prims.append(T(x + 8, by, label_w, 20, f"Difference ({ex['unit']}), 95% CI", size=11, color="grey"))
    return prims


def ex_table(x, y, w, h, ex):
    cols = ex.get("columns", [])
    rows = ex.get("rows", [])
    if not cols:
        return []
    highlight = set(ex.get("highlight_rows", []))
    weights, min_w = [], []
    for c in range(len(cols)):
        texts = [cell_text(r[c]) for r in rows if c < len(r)] + [cols[c]]
        weights.append(min(max(max(len(t) for t in texts), 6), 42))
        longest_word = max((len(word) for t in texts for word in t.split()), default=4)
        min_w.append(longest_word * 16 * 0.6 + 24)
    col_w = [w * wt / sum(weights) for wt in weights]
    # No column narrower than its longest word; take the space from the widest columns.
    short = sum(max(0, m - cw) for m, cw in zip(min_w, col_w))
    if short:
        spare = [max(0, cw - m) for m, cw in zip(min_w, col_w)]
        total_spare = sum(spare) or 1
        col_w = [max(m, cw) if cw < m else cw - short * s / total_spare for m, cw, s in zip(min_w, col_w, spare)]
    for size in (16, 15, 14, 13, 12, 11):
        head_h = max(text_height(c, size, cw - 20) for c, cw in zip(cols, col_w)) + 18
        body_h = [max(text_height(cell_text(r[c]) if c < len(r) else "", size, col_w[c] - 20)
                      for c in range(len(cols))) + 22 for r in rows]
        if head_h + sum(body_h) <= h:
            break
    # Use the space: give rows breathing room instead of leaving the bottom of the slide empty.
    free = h - head_h - sum(body_h)
    if free > 0 and rows:
        extra = min(free / len(rows), 26)
        body_h = [bh + extra for bh in body_h]
    data = [[{"text": c, "bold": True, "color": "white"} for c in cols]] + [list(r) for r in rows]
    fills = ["ink"] + [("accent_soft" if i in highlight else ("bg_soft" if i % 2 else None)) for i in range(len(rows))]
    for i in highlight:
        data[i + 1] = [{"text": cell_text(c), "bold": True, "color": c.get("color") if isinstance(c, dict) else None}
                       for c in data[i + 1]]
    return [TABLE(x, y, col_w, [head_h] + body_h, data, size, fills)]


def ex_matrix(x, y, w, h, ex):
    side = min(w - 150, h - 56)
    px, py = x + 70, y
    half = side / 2
    q = ex.get("quadrants", {})
    prims = []
    for key, qx, qy in (("tl", 0, 0), ("tr", 1, 0), ("bl", 0, 1), ("br", 1, 1)):
        prims.append(R(px + qx * half + 1, py + qy * half + 1, half - 2, half - 2, fill="bg_soft"))
        if q.get(key):
            prims.append(T(px + qx * half + 12, py + qy * half + 10, half - 24, 20, q[key].upper(), size=11,
                           color="grey", bold=True))
    xa, ya = ex.get("x", {}), ex.get("y", {})
    prims.append(T(x, py, 64, 20, ya.get("high", "High"), size=12, color="grey", align="right"))
    prims.append(T(x, py + side - 18, 64, 20, ya.get("low", "Low"), size=12, color="grey", align="right"))
    prims.append(T(x, py + half - 30, 64, 60, ya.get("name", ""), size=12, bold=True, align="right", valign="middle"))
    prims.append(T(px, py + side + 6, 120, 20, xa.get("low", "Low"), size=12, color="grey"))
    prims.append(T(px + side - 120, py + side + 6, 120, 20, xa.get("high", "High"), size=12, color="grey",
                   align="right"))
    prims.append(T(px, py + side + 26, side, 20, xa.get("name", "") + " →", size=12, bold=True, align="center"))
    for p in ex.get("points", []):
        cx = px + float(p.get("x", 0.5)) * side
        cy = py + (1 - float(p.get("y", 0.5))) * side
        hl = p.get("highlight")
        prims.append(E(cx - 9, cy - 9, 18, 18, fill="accent" if hl else "grey_bar", line="white", line_w=2))
        prims.append(T(cx + 14, cy - 10, 170, 20, p.get("label", ""), size=13, bold=bool(hl),
                       color="ink" if hl else "grey_dark"))
    note_x = px + side + 30
    if ex.get("basis") and x + w - note_x > 160:
        prims.append(T(note_x, py, x + w - note_x, 16, "HOW WE PLACED THEM", size=11, color="grey", bold=True))
        prims.append(T(note_x, py + 22, x + w - note_x, side, ex["basis"], size=13, color="grey_dark", lh=1.35))
    return prims


def ex_options(x, y, w, h, ex):
    crit = ex.get("criteria", [])
    opts = ex.get("options", [])
    rec = ex.get("recommended")
    name_w, verdict_w = w * 0.3, w * 0.2
    cw = (w - name_w - verdict_w) / max(1, len(crit))
    head_h = 46
    row_h = min(70, (h - head_h - 30) / max(1, len(opts)))
    prims = []
    for c, label in enumerate(crit):
        prims.append(T(x + name_w + c * cw, y, cw, head_h, label, size=13, bold=True, color="grey_dark",
                       align="center", valign="bottom"))
    prims.append(L(x, y + head_h + 6, x + w, y + head_h + 6, color="grey_light"))
    for i, o in enumerate(opts):
        ry = y + head_h + 12 + i * row_h
        if i == rec:
            prims.append(R(x, ry, w, row_h - 4, fill="accent_soft"))
            prims.append(R(x, ry, 5, row_h - 4, fill="accent"))
        prims.append(T(x + 16, ry, name_w - 20, row_h - 4, o.get("name", ""), size=15, bold=i == rec,
                       valign="middle"))
        for c, score in enumerate(o.get("scores", [])):
            d = 26
            prims.append(HARVEY(x + name_w + c * cw + cw / 2 - d / 2, ry + (row_h - 4) / 2 - d / 2, d, score))
        prims.append(T(x + w - verdict_w, ry, verdict_w - 8, row_h - 4, o.get("verdict", ""), size=14,
                       bold=i == rec, color="accent" if i == rec else "grey_dark", valign="middle"))
    ly = y + head_h + 12 + len(opts) * row_h + 4
    prims.append(T(x, ly, w, 18, "Filled circle = strongest on that criterion; empty = weakest", size=11, color="grey"))
    return prims


def ex_issue_tree(x, y, w, h, ex):
    branches = ex.get("branches", [])
    if not branches:
        return []
    root_w, br_x, br_w = w * 0.26, x + w * 0.33, w * 0.3
    ch_x, ch_w = x + w * 0.67, w * 0.33
    row_h = h / len(branches)
    mid = y + h / 2
    root_h = max(80, text_height(ex.get("root", ""), 16, root_w - 28) + 30)
    prims = [R(x, mid - root_h / 2, root_w, root_h, fill="ink", radius=6),
             T(x + 14, mid - root_h / 2, root_w - 28, root_h, ex.get("root", ""), size=16, bold=True, color="white",
               valign="middle", font="head")]
    spine_x = x + root_w + (br_x - x - root_w) / 2
    mids = [y + i * row_h + row_h / 2 for i in range(len(branches))]
    prims.append(L(x + root_w, mid, spine_x, mid, color="grey", w=1.5))
    prims.append(L(spine_x, min(mids), spine_x, max(mids), color="grey", w=1.5))
    for b, by in zip(branches, mids):
        status = b.get("status", "open")
        col = STATUS_COLOR.get(status, "grey")
        bh = min(row_h - 12, 70)
        prims.append(L(spine_x, by, br_x, by, color="grey", w=1.5))
        prims.append(R(br_x, by - bh / 2, br_w, bh, fill="white", line=col, line_w=2, radius=6))
        prims.append(T(br_x + 14, by - bh / 2 + 6, br_w - 28, bh - 26, b.get("label", ""), size=14, bold=True,
                       valign="middle"))
        prims.append(T(br_x + 14, by + bh / 2 - 22, br_w - 28, 16, status.upper(), size=10, bold=True, color=col))
        kids = b.get("children", [])
        if kids:
            prims.append(T(ch_x, by - row_h / 2 + 4, ch_w, row_h - 8, "\n".join("• " + k for k in kids), size=13,
                           color="grey_dark", valign="middle", lh=1.3))
    return prims


def ex_roadmap(x, y, w, h, ex):
    start, end = int(ex.get("start", 1)), int(ex.get("end", 12))
    units = max(1, end - start + 1)
    lanes = ex.get("lanes", [])
    label_w = 190
    x0, tw = x + label_w, w - label_w
    uw = tw / units
    head_h, gate_h = 30, 46
    lane_h = min(96, (h - head_h - gate_h) / max(1, len(lanes)))
    step = 1 if units <= 12 else (2 if units <= 24 else 4)
    prims = []
    for u in range(start, end + 1, step):
        prims.append(T(x0 + (u - start) * uw, y, uw * step, 20, f"{ex.get('unit', 'Week')} {u}", size=11,
                       color="grey"))
    palette = ["accent", "ink", "accent_mid"]
    for i, lane in enumerate(lanes):
        ly = y + head_h + i * lane_h
        if i % 2 == 0:
            prims.append(R(x, ly, w, lane_h, fill="bg_soft"))
        prims.append(T(x + 10, ly, label_w - 20, lane_h, lane.get("name", ""), size=14, bold=True, valign="middle"))
        bars = sorted(lane.get("bars", []), key=lambda b: b["start"])
        occupied = x0
        for k, b in enumerate(bars):
            bx = x0 + (b["start"] - start) * uw + 3
            bw = (b["end"] - b["start"] + 1) * uw - 6
            bh = lane_h * 0.5
            by = ly + lane_h * 0.12
            prims.append(R(bx, by, bw, bh, fill=palette[i % 3], radius=4))
            label = b.get("label", "") + (f" · {b['owner']}" if b.get("owner") else "")
            if text_lines(label, 13, bw - 16) <= 2:
                prims.append(T(bx + 8, by, bw - 16, bh, label, size=13, bold=True, color="white", valign="middle",
                               lh=1.15))
                occupied = bx + bw
                continue
            # Too narrow: put the label under the bar, without running into the next bar's label.
            nxt = x0 + (bars[k + 1]["start"] - start) * uw if k + 1 < len(bars) else x + w
            room_right = nxt - bx - 10
            if room_right >= 120:
                lw = min(room_right, 320)
                prims.append(T(bx, by + bh + 4, lw, 16, truncate(label, int(lw / (11 * 0.52))), size=11))
                occupied = bx + lw
            else:
                lx = max(occupied + 10, x0)
                lw = bx + bw - lx
                prims.append(T(lx, by + bh + 4, lw, 16, truncate(label, int(lw / (11 * 0.52))), size=11,
                               align="right"))
                occupied = bx + bw
    lanes_bottom = y + head_h + len(lanes) * lane_h
    last_x = -999
    level = 0
    for g in sorted(ex.get("gates", []), key=lambda g: g["at"]):
        gx = min(x0 + (g["at"] - start + 1) * uw, x + w - 2)
        prims.append(L(gx, y + head_h - 4, gx, lanes_bottom + 6, color="gate", w=2, dash=True))
        prims.append(DIAMOND(gx - 8, y + head_h - 12, 16, 16, fill="gate"))
        level = level + 1 if gx - last_x < 200 else 0
        lx = max(x, min(gx - 100, x + w - 200))
        align = "center" if lx == gx - 100 else ("right" if lx > gx - 100 else "left")
        prims.append(T(lx, lanes_bottom + 10 + (level % 2) * 38, 200, 36, "◆ " + g.get("label", ""), size=12,
                       bold=True, color="gate", align=align, lh=1.2))
        last_x = gx
    return prims


def ex_kpi(x, y, w, h, ex):
    rows = ex.get("rows", [])
    has_owner = any(r.get("owner") for r in rows)
    cols = ["Metric", "Baseline", "Target", "Decision gate"] + (["Owner"] if has_owner else [])
    table_rows = []
    for r in rows:
        row = [{"text": r.get("metric", ""), "bold": True}, r.get("baseline", ""),
               {"text": r.get("target", ""), "bold": True, "color": "accent"}, r.get("gate", "")]
        if has_owner:
            row.append(r.get("owner", ""))
        table_rows.append(row)
    return ex_table(x, y, w, h, {"columns": cols, "rows": table_rows})


def ex_evidence_map(x, y, w, h, ex):
    rows = []
    for r in ex.get("rows", []):
        strength = r.get("strength", "unknown")
        status = r.get("status", "unknown")
        rows.append([r.get("claim", ""),
                     {"text": "● " + strength.capitalize(), "bold": True,
                      "color": strength if strength in EVIDENCE_LABEL else "grey"},
                     {"text": status.capitalize(), "bold": True, "color": STATUS_COLOR.get(status, "grey")},
                     r.get("close_by", "")])
    return ex_table(x, y, w, h, {"columns": ["Claim", "Evidence", "Status", "How to close the gap"], "rows": rows})


def ex_bullets(x, y, w, h, ex):
    items = ex.get("items", [])
    sizes = [(item.get("head", ""), item.get("text", "")) for item in items]
    heights = [((text_height(hd, 20, w - 34, lh=1.25) if hd else 0), (text_height(bd, 16, w - 34, lh=1.4) if bd else 0))
               for hd, bd in sizes]
    free = h - sum(a + b + 6 for a, b in heights)
    gap = max(18, min(52, free / max(1, len(items))))
    prims = []
    yy = y
    for (head, body), (hh, bh) in zip(sizes, heights):
        if yy + hh + bh > y + h:
            break
        prims.append(R(x, yy + 8, 10, 10, fill="accent"))
        if head:
            prims.append(T(x + 30, yy, w - 30, hh, head, size=20, bold=True, lh=1.25))
        if body:
            prims.append(T(x + 30, yy + hh + 6, w - 30, bh, body, size=16, color="grey_dark", lh=1.4))
        yy += hh + bh + 6 + gap
    return prims


def ex_hero(x, y, w, h, ex):
    value, unit = str(ex.get("value", "")), ex.get("unit", "")
    runs = [{"text": value, "size": 128}]
    if unit:
        runs.append({"text": " " + unit, "size": 52})
    prims = [T(x, y + 10, w, 160, size=128, color="accent", font="head", bold=True, runs=runs, lh=1.0)]
    lh = text_height(ex.get("label", ""), 26, w, lh=1.25)
    prims.append(T(x, y + 180, w, lh, ex.get("label", ""), size=26, font="head", lh=1.25))
    if ex.get("context"):
        prims.append(T(x, y + 196 + lh, w, 80, ex["context"], size=15, color="grey_dark", lh=1.4))
    return prims


EXHIBITS = {"bar": ex_bar, "dot_ci": ex_dot_ci, "table": ex_table, "matrix_2x2": ex_matrix,
            "options": ex_options, "issue_tree": ex_issue_tree, "roadmap": ex_roadmap, "kpi": ex_kpi,
            "evidence_map": ex_evidence_map, "bullets": ex_bullets, "hero_stat": ex_hero}


def exhibit(box, ex):
    fn = EXHIBITS.get((ex or {}).get("kind"))
    return fn(*box, ex) if fn else []


# ---------- layouts ----------

def lay_cover(slide, deck):
    m = deck.get("meta", {})
    title = slide.get("title") or m.get("title", "")
    size = fit_size(title, 980, 3, [48, 42, 36], char_w=0.5)
    th = text_height(title, size, 980, lh=1.15, char_w=0.5)
    prims = [R(W - 28, 0, 28, H, fill="accent"),
             T(MX, 120, 600, 18, m.get("prepared_by", "").upper(), size=12, color="accent", bold=True),
             R(MX, 196, 84, 6, fill="accent"),
             T(MX, 222, 1000, th, title, size=size, font="head", lh=1.15)]
    sub = slide.get("subtitle") or m.get("subtitle")
    if sub:
        prims.append(T(MX, 222 + th + 18, 1000, 90, sub, size=22, color="grey_dark", lh=1.35))
    line = " · ".join(v for v in (m.get("client"), m.get("date")) if v)
    prims.append(T(MX, 596, 900, 20, line, size=14, color="grey_dark"))
    if m.get("note"):
        prims.append(T(MX, 624, 1000, 40, m["note"], size=12, color="grey", italic=True))
    if m.get("evidence") in EVIDENCE_LABEL:
        prims += evidence_badge(MX, 664, m["evidence"], size=11)
    return prims


def lay_section(slide, deck):
    return [R(0, 0, W, H, fill="ink"),
            R(MX, 300, 84, 6, fill="accent"),
            T(MX, 326, 1100, 160, slide.get("title", ""), size=40, color="white", font="head", lh=1.2)]


def lay_exec(slide, deck, page):
    prims = header(slide)
    left_w = 730
    box_x, box_w = MX + left_w + 40, CONTENT_W - left_w - 40
    bottom = FOOT_Y - 16
    y = BODY_Y + 8
    points = slide.get("points", [])[:4]
    avail = bottom - y
    tw = left_w - 60
    for hsize, dsize in ((21, 16), (19, 15), (18, 14), (17, 13)):
        blocks = [(text_height(p.get("headline", ""), hsize, tw, lh=1.25),
                   text_height(p.get("detail", ""), dsize, tw, lh=1.4) if p.get("detail") else 0) for p in points]
        need = sum(max(40, a + b + 8) for a, b in blocks)
        if need + 16 * len(points) <= avail:
            break
    gap = max(16, min(44, (avail - need) / max(1, len(points))))
    for i, (p, (hh, dh)) in enumerate(zip(points, blocks), 1):
        prims.append(E(MX, y, 38, 38, fill="accent"))
        prims.append(T(MX, y, 38, 38, str(i), size=17, bold=True, color="white", align="center", valign="middle"))
        prims.append(T(MX + 58, y + 4, tw, hh, p.get("headline", ""), size=hsize, bold=True, lh=1.25))
        if dh:
            prims.append(T(MX + 58, y + 10 + hh, tw, dh, p["detail"], size=dsize, color="grey_dark", lh=1.4))
        y += max(40, hh + dh + 8) + gap
        if i < len(points):
            prims.append(L(MX + 58, y - gap / 2, MX + left_w, y - gap / 2, color="grey_light"))
    prims.append(R(box_x, BODY_Y + 8, box_w, bottom - BODY_Y - 8, fill="ink", radius=4))
    prims.append(R(box_x, BODY_Y + 8, box_w, 6, fill="accent"))
    prims.append(T(box_x + 30, BODY_Y + 38, box_w - 60, 16, "RECOMMENDATION", size=12, bold=True, color="accent_mid"))
    rec = slide.get("recommendation", "")
    rsize = fit_size(rec, box_w - 60, 8, [28, 26, 24, 22, 20, 18], char_w=0.5)
    prims.append(T(box_x + 30, BODY_Y + 66, box_w - 60, bottom - BODY_Y - 120, rec, size=rsize, color="white",
                   font="head", lh=1.3, valign="middle"))
    ev = slide.get("evidence")
    if ev in EVIDENCE_LABEL:
        prims.append(E(box_x + 30, bottom - 34, 10, 10, fill=ev))
        prims.append(T(box_x + 46, bottom - 37, box_w - 76, 16, EVIDENCE_LABEL[ev] + " overall", size=12, bold=True,
                       color="accent_soft"))
    prims += footer(slide, deck, page)
    return prims


def lay_hero(slide, deck, page):
    prims = header(slide)
    bottom = SOWHAT_Y - 14 if slide.get("so_what") else FOOT_Y - 16
    has_rail = bool(slide.get("takeaways"))
    w = EXHIBIT_W_WITH_RAIL if has_rail else CONTENT_W
    prims += ex_hero(MX, BODY_Y + 10, w, bottom - BODY_Y - 10, slide.get("exhibit", {}))
    if has_rail:
        prims += takeaways_rail(slide["takeaways"], BODY_Y + 10, bottom)
    if slide.get("so_what"):
        prims += so_what_bar(slide["so_what"])
    prims += footer(slide, deck, page)
    return prims


def lay_content(slide, deck, page):
    prims = header(slide)
    bottom = SOWHAT_Y - 14 if slide.get("so_what") else FOOT_Y - 16
    has_rail = slide.get("layout") != "full" and bool(slide.get("takeaways"))
    w = EXHIBIT_W_WITH_RAIL if has_rail else CONTENT_W
    prims += exhibit((MX, BODY_Y + 10, w, bottom - BODY_Y - 10), slide.get("exhibit"))
    if has_rail:
        prims += takeaways_rail(slide["takeaways"], BODY_Y + 10, bottom)
    if slide.get("so_what"):
        prims += so_what_bar(slide["so_what"])
    prims += footer(slide, deck, page)
    return prims


def lay_sources(slide, deck, page):
    s = dict(slide)
    s.setdefault("title", "Sources")
    prims = header(s)
    sources = deck.get("sources", [])
    col_w = (CONTENT_W - 40) / 2
    entries = [f"[{x.get('n')}] {x.get('label', '')} — {truncate(x.get('url', ''), 80)}" for x in sources]
    size = 12
    heights = [text_height(e, size, col_w, lh=1.3, char_w=0.5) + 8 for e in entries]
    if sum(heights) / 2 > FOOT_Y - BODY_Y - 30:
        size = 10
        heights = [text_height(e, size, col_w, lh=1.3, char_w=0.5) + 6 for e in entries]
    half = sum(heights) / 2
    y, col, acc = BODY_Y + 6, 0, 0
    for e, hgt in zip(entries, heights):
        if col == 0 and acc + hgt > half + 1 and acc > 0:
            col, y = 1, BODY_Y + 6
        prims.append(T(MX + col * (col_w + 40), y, col_w, hgt, e, size=size, color="grey_dark", lh=1.3))
        y += hgt
        acc += hgt
    prims.append(T(W - MX - 40, FOOT_Y, 40, 14, str(page), size=10, color="grey", align="right"))
    return prims


def build(deck):
    """Returns [{"prims": [...], "notes": str, "id": str}] for every slide in order."""
    out = []
    for page, slide in enumerate(deck.get("slides", []), 1):
        layout = slide.get("layout", "standard")
        if layout == "cover":
            prims = lay_cover(slide, deck)
        elif layout == "section":
            prims = lay_section(slide, deck)
        elif layout == "exec_summary":
            prims = lay_exec(slide, deck, page)
        elif layout == "hero":
            prims = lay_hero(slide, deck, page)
        elif layout == "sources":
            prims = lay_sources(slide, deck, page)
        else:
            prims = lay_content(slide, deck, page)
        out.append({"prims": prims, "notes": slide.get("notes", ""), "id": slide.get("id", f"s{page}"),
                    "dark": layout == "section"})
    return out
