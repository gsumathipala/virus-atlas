"""Visual QA: inline the app's CSS into the emitted SVGs and rasterize them.

svglib honours presentation attributes and inline style="", but not external
stylesheets, CSS custom properties or color-mix(). So this resolves the figure
rules from app.css into literal inline styles first. It is a QA tool, not part
of the app -- the browser does all of this natively.
"""

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas

HERE = Path(__file__).resolve().parent
CSS = Path("/Users/saranga/virus-atlas/static/css/app.css")
SVG_DIR = HERE / "svg"
PNG_DIR = HERE / "png"

ET.register_namespace("", "http://www.w3.org/2000/svg")
SVG_NS = "{http://www.w3.org/2000/svg}"


# ----------------------------------------------------------------- CSS values

def parse_root_vars(css):
    """Custom properties from the first :root block (the dark theme)."""
    out = {}
    # Several :root blocks exist (base + figure palette); merge them all, but
    # skip :root[data-theme="light"] so we render the dark theme.
    for m in re.finditer(r":root\s*\{(.*?)\}", css, re.S):
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
            out[name] = value.strip()
    return out


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parse_color(c):
    c = c.strip()
    if c.startswith("#"):
        return hex_to_rgb(c), 1.0
    m = re.match(r"rgba?\(([^)]+)\)", c)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        rgb = tuple(int(float(p)) for p in parts[:3])
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return rgb, a
    if c == "transparent":
        return (0, 0, 0), 0.0
    return None, None


def resolve_vars(value, vars_, depth=0):
    if depth > 12:
        return value
    def sub(m):
        name, fallback = m.group(1), m.group(2)
        v = vars_.get(name)
        if v is None:
            return (fallback or "").strip()
        return resolve_vars(v, vars_, depth + 1)
    return re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", sub, value)


def resolve_color_mix(value):
    """color-mix(in srgb, C p%, transparent) -> rgba(...)  (the only form used)."""
    pattern = re.compile(
        r"color-mix\(\s*in\s+srgb\s*,\s*([^,]+?)\s+([\d.]+)%\s*,\s*([^)]+?)\s*\)")
    while True:
        m = pattern.search(value)
        if not m:
            return value
        c1, pct, c2 = m.group(1).strip(), float(m.group(2)), m.group(3).strip()
        rgb1, a1 = parse_color(c1)
        rgb2, a2 = parse_color(c2)
        if rgb1 is None or rgb2 is None:
            return value.replace(m.group(0), "#888888")
        f = pct / 100.0
        rgb = tuple(round(rgb1[i] * f + rgb2[i] * (1 - f)) for i in range(3))
        a = a1 * f + a2 * (1 - f)
        value = value[:m.start()] + f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{round(a, 3)})" + value[m.end():]


def flatten(value, vars_):
    return resolve_color_mix(resolve_vars(value, vars_)).strip()


# ------------------------------------------------------------- CSS rule model

PROPS = {
    "fill", "stroke", "stroke-width", "stroke-dasharray", "stroke-linecap",
    "stroke-linejoin", "opacity", "fill-opacity", "stroke-opacity",
    "font-family", "font-size", "font-weight", "letter-spacing",
    "text-transform",
}


def parse_rules(css, vars_):
    """[(selector_parts, {prop: value})] for selectors we can evaluate."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css, flags=re.S)
    rules = []
    for sel_blob, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        decls = {}
        for prop, value in re.findall(r"([-\w]+)\s*:\s*([^;]+)", body):
            prop = prop.strip()
            if prop in PROPS:
                decls[prop] = flatten(value, vars_)
        if not decls:
            continue
        for sel in sel_blob.split(","):
            sel = sel.strip()
            if not sel or sel.startswith(("@", ":root", "html", "body")):
                continue
            rules.append((sel, decls))
    return rules


SIMPLE = re.compile(r'^([a-zA-Z][\w-]*)?((?:\.[\w-]+)+)(?:\[([\w-]+)="([^"]+)"\])?$')


def sel_matches_el(sel, classes, attrs, tag):
    """Match one compound selector against an element."""
    sel = sel.strip()
    if sel == "*":
        return True
    if sel in (tag, f"{SVG_NS}{tag}"):
        return True
    m = SIMPLE.match(sel)
    if not m:
        return False
    eltag, cls, attr, val = m.groups()
    if eltag and eltag != tag:
        return False
    need = {c for c in cls.split(".") if c}
    if not need <= classes:
        return False
    if attr and attrs.get(attr) != val:
        return False
    return True


def collect(root):
    """Element -> (classes, attrs, tag, ancestor chain)."""
    out = []
    def walk(el, chain):
        tag = el.tag.replace(SVG_NS, "")
        classes = set((el.get("class") or "").split())
        rec = (el, classes, el.attrib, tag, list(chain))
        out.append(rec)
        for child in el:
            walk(child, chain + [(classes, el.attrib, tag)])
    walk(root, [])
    return out


def apply_css(svg_text, rules):
    root = ET.fromstring(svg_text)
    for el, classes, attrs, tag, chain in collect(root):
        style = {}
        for sel, decls in rules:
            parts = sel.split()
            if not sel_matches_el(parts[-1], classes, attrs, tag):
                continue
            # Ancestor parts must appear in order somewhere up the chain.
            ok, idx = True, 0
            for part in parts[:-1]:
                found = False
                while idx < len(chain):
                    acls, aattrs, atag = chain[idx]
                    idx += 1
                    if sel_matches_el(part, acls, aattrs, atag):
                        found = True
                        break
                if not found:
                    ok = False
                    break
            if ok:
                style.update(decls)
        if style:
            for prop in ("fill", "stroke"):
                v = style.get(prop, "")
                m = re.match(r"rgba\(([^)]+)\)", v.strip())
                if m:
                    parts = [x.strip() for x in m.group(1).split(",")]
                    style[prop] = f"rgb({parts[0]},{parts[1]},{parts[2]})"
                    if len(parts) > 3:
                        a = float(parts[3])
                        if a == 0:
                            style[prop] = "none"
                        else:
                            style[f"{prop}-opacity"] = str(a)
            merged = "; ".join(f"{k}: {v}" for k, v in style.items())
            existing = el.get("style")
            el.set("style", f"{merged}; {existing}" if existing else merged)
    return ET.tostring(root, encoding="unicode")


def main():
    css = CSS.read_text()
    vars_ = parse_root_vars(css)
    rules = parse_rules(css, vars_)
    print(f"{len(vars_)} css vars, {len(rules)} usable rules")

    PNG_DIR.mkdir(exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(SVG_DIR.glob("*.svg"))
    if only:
        files = [f for f in files if only in f.name]

    # One PDF contact sheet: cairo is unavailable, but reportlab's PDF backend
    # is pure Python and a PDF can be inspected page by page.
    out_pdf = PNG_DIR / (f"sheet-{only}.pdf" if only else "sheet.pdf")
    PW, PH = A4[1], A4[0]              # landscape
    c = rl_canvas.Canvas(str(out_pdf), pagesize=(PW, PH))
    ok = 0
    for f in files:
        try:
            svg = apply_css(f.read_text(), rules)
            tmp = PNG_DIR / (f.stem + ".styled.svg")
            tmp.write_text(svg)
            drawing = svg2rlg(str(tmp))
            tmp.unlink()
            if drawing is None or not drawing.width:
                print(f"  {f.name}: svglib returned nothing")
                continue
            c.setFillColorRGB(0.059, 0.082, 0.169)
            c.rect(0, 0, PW, PH, stroke=0, fill=1)
            margin = 46
            scale = min((PW - margin * 2) / drawing.width,
                        (PH - margin * 2 - 26) / drawing.height)
            drawing.scale(scale, scale)
            drawing.width *= scale
            drawing.height *= scale
            renderPDF.draw(drawing, c,
                           (PW - drawing.width) / 2,
                           (PH - drawing.height) / 2 - 10)
            c.setFillColorRGB(0.91, 0.925, 0.973)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(margin, PH - 30, f.stem)
            c.showPage()
            ok += 1
            print(f"  page {ok}: {f.stem}  {drawing.width:.0f}x{drawing.height:.0f}")
        except Exception as exc:
            print(f"  {f.name}: FAILED {type(exc).__name__}: {exc}")
    c.save()
    print(f"wrote {out_pdf} with {ok} pages")


if __name__ == "__main__":
    main()
