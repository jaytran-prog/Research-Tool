"""HTML backend: draws layout primitives as absolutely positioned elements. Prints to PDF one slide per page."""
import html

from deck_layout import W, H, bar_prims, cell_text


def _c(theme, c):
    if not c:
        return None
    return c if c.startswith("#") else theme["colors"].get(c, c)


def _font(theme, key):
    return theme["fonts"]["head_css" if key == "head" else "body_css"]


def _box(p):
    return f"left:{p['x']:.1f}px;top:{p['y']:.1f}px;width:{p['w']:.1f}px;height:{p['h']:.1f}px;"


def _text(p, theme):
    justify = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}[p["valign"]]
    style = (_box(p) + f"font-size:{p['size']}px;color:{_c(theme, p['color'])};font-family:{_font(theme, p['font'])};"
             f"font-weight:{700 if p['bold'] else 400};text-align:{p['align']};justify-content:{justify};"
             f"line-height:{p['lh']};font-style:{'italic' if p['italic'] else 'normal'};")
    spans = []
    for r in p["runs"]:
        s = ""
        if r.get("bold") is not None:
            s += f"font-weight:{700 if r['bold'] else 400};"
        if r.get("color"):
            s += f"color:{_c(theme, r['color'])};"
        if r.get("size"):
            s += f"font-size:{r['size']}px;"
        if r.get("italic"):
            s += "font-style:italic;"
        body = html.escape(r.get("text", "")).replace("\n", "<br>")
        spans.append(f'<span style="{s}">{body}</span>' if s else body)
    return f'<div class="t" style="{style}"><div>{"".join(spans)}</div></div>'


def _rect(p, theme, round_=False):
    fill = _c(theme, p.get("fill"))
    style = _box(p)
    if p.get("hatch") and fill:
        style += f"background:repeating-linear-gradient(135deg,{fill} 0 5px,#fff 5px 9px);border:1.5px solid {fill};"
    elif fill:
        style += f"background:{fill};"
    if p.get("line"):
        style += f"border:{p['line_w']}px solid {_c(theme, p['line'])};"
    radius = "50%" if round_ else f"{p.get('radius', 0)}px"
    style += f"border-radius:{radius};"
    return f'<div class="s" style="{style}"></div>'


def _line(p, theme):
    dash = ' stroke-dasharray="6 5"' if p["dash"] else ""
    return (f'<svg class="l" width="{W}" height="{H}"><line x1="{p["x1"]:.1f}" y1="{p["y1"]:.1f}" '
            f'x2="{p["x2"]:.1f}" y2="{p["y2"]:.1f}" stroke="{_c(theme, p["color"])}" stroke-width="{p["w"]}"{dash}/></svg>')


def _diamond(p, theme):
    return f'<div class="s" style="{_box(p)}background:{_c(theme, p["fill"])};transform:rotate(45deg) scale(.8);"></div>'


def _harvey(p, theme):
    pct = p["score"] * 25
    acc = _c(theme, "ink")
    style = (f"left:{p['x']:.1f}px;top:{p['y']:.1f}px;width:{p['d']}px;height:{p['d']}px;border-radius:50%;"
             f"border:2px solid {acc};background:conic-gradient({acc} 0 {pct}%,#fff {pct}% 100%);box-sizing:border-box;")
    return f'<div class="s" style="{style}"></div>'


def _table(p, theme):
    out = [f'<table class="tb" style="left:{p["x"]:.1f}px;top:{p["y"]:.1f}px;width:{p["w"]:.1f}px;'
           f'font-size:{p["size"]}px;font-family:{_font(theme, "body")};"><colgroup>']
    out += [f'<col style="width:{w:.1f}px">' for w in p["col_w"]]
    out.append("</colgroup>")
    for r, (row, h) in enumerate(zip(p["rows"], p["row_h"])):
        fill = _c(theme, p["fills"][r])
        out.append(f'<tr style="height:{h:.1f}px;{f"background:{fill};" if fill else ""}">')
        for cell in row:
            s = ""
            if isinstance(cell, dict):
                if cell.get("bold"):
                    s += "font-weight:700;"
                if cell.get("color"):
                    s += f"color:{_c(theme, cell['color'])};"
            out.append(f'<td style="{s}">{html.escape(cell_text(cell))}</td>')
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


def _prim(p, theme):
    t = p["type"]
    if t == "text":
        return _text(p, theme)
    if t == "rect":
        return _rect(p, theme)
    if t == "ellipse":
        return _rect(p, theme, round_=True)
    if t == "line":
        return _line(p, theme)
    if t == "diamond":
        return _diamond(p, theme)
    if t == "harvey":
        return _harvey(p, theme)
    if t == "table":
        return _table(p, theme)
    if t == "bar":
        return "".join(_prim(q, theme) for q in bar_prims(p["x"], p["y"], p["w"], p["h"], p["spec"]))
    return ""


CSS = """
:root{--s:1}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#E9EDF3;font-family:%(body)s;color:%(ink)s}
.deck{display:flex;flex-direction:column;align-items:center;gap:28px;padding:28px 0}
.frame{width:calc(%(w)spx * var(--s));height:calc(%(h)spx * var(--s))}
.slide{position:relative;width:%(w)spx;height:%(h)spx;background:#fff;overflow:hidden;transform:scale(var(--s));
transform-origin:0 0;box-shadow:0 6px 24px rgba(11,31,51,.12)}
.t{position:absolute;display:flex;flex-direction:column;overflow:visible;white-space:normal;overflow-wrap:anywhere}
.s{position:absolute}
.l{position:absolute;left:0;top:0;pointer-events:none;overflow:visible}
.tb{position:absolute;border-collapse:collapse;table-layout:fixed;color:%(ink)s}
.tb td{padding:8px 10px;vertical-align:middle;line-height:1.3}
.bar{position:fixed;top:0;left:0;right:0;height:4px;background:%(accent)s;transform-origin:0 0;z-index:9}
@page{size:%(w)spx %(h)spx;margin:0}
@media print{body{background:#fff}.deck{display:block;padding:0}.frame{width:%(w)spx;height:%(h)spx;
page-break-after:always;break-after:page}.slide{transform:none;box-shadow:none}.bar{display:none}}
"""

JS = """
const fit=()=>{const s=Math.min(1,(window.innerWidth-48)/%(w)s);document.documentElement.style.setProperty('--s',s)};
fit();addEventListener('resize',fit);
const frames=[...document.querySelectorAll('.frame')];
addEventListener('keydown',e=>{const y=scrollY+innerHeight/2;let i=frames.findIndex(f=>f.offsetTop+f.offsetHeight>y);
if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();frames[Math.min(i+1,frames.length-1)].scrollIntoView({behavior:'smooth',block:'center'})}
if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();frames[Math.max(i-1,0)].scrollIntoView({behavior:'smooth',block:'center'})}});
addEventListener('scroll',()=>{const p=scrollY/(document.body.scrollHeight-innerHeight||1);document.querySelector('.bar').style.transform=`scaleX(${p})`});
"""


def render_html(built, deck, theme):
    title = html.escape(deck.get("meta", {}).get("title", "Deck"))
    vals = {"w": W, "h": H, "body": theme["fonts"]["body_css"], "ink": theme["colors"]["ink"],
            "accent": theme["colors"]["accent"]}
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
             f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>'
             f"<style>{CSS % vals}</style></head><body><div class=\"bar\"></div><div class=\"deck\">"]
    for s in built:
        parts.append(f'<div class="frame"><section class="slide" id="{html.escape(s["id"])}">')
        parts += [_prim(p, theme) for p in s["prims"]]
        parts.append("</section></div>")
    parts.append(f"</div><script>{JS % vals}</script></body></html>")
    return "".join(parts)
