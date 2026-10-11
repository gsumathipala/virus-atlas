"""Lay emitted SVGs out in a grid, one single-page PDF per sheet, then PNG."""
import subprocess, sys
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas as rl_canvas
import rasterize as R

HERE = Path(__file__).resolve().parent
OUT = HERE / "png"; OUT.mkdir(exist_ok=True)

def sheet(files, name, cols, rows, cell=(560, 400)):
    css = R.CSS.read_text(); vars_ = R.parse_root_vars(css); rules = R.parse_rules(css, vars_)
    cw, ch = cell
    PW, PH = cols * cw, rows * ch
    pdf = OUT / f"{name}.pdf"
    c = rl_canvas.Canvas(str(pdf), pagesize=(PW, PH))
    c.setFillColorRGB(0.059, 0.082, 0.169); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    for i, f in enumerate(files[: cols * rows]):
        col, row = i % cols, i // cols
        x0, y0 = col * cw, PH - (row + 1) * ch
        svg = R.apply_css(f.read_text(), rules)
        tmp = OUT / (f.stem + ".tmp.svg"); tmp.write_text(svg)
        d = svg2rlg(str(tmp)); tmp.unlink()
        if d is None or not d.width: continue
        pad = 20
        s = min((cw - pad*2) / d.width, (ch - pad*2 - 20) / d.height)
        d.scale(s, s); d.width *= s; d.height *= s
        renderPDF.draw(d, c, x0 + (cw - d.width)/2, y0 + (ch - d.height)/2 - 8)
        c.setFillColorRGB(0.64, 0.67, 0.77); c.setFont("Helvetica", 10)
        c.drawString(x0 + pad, y0 + ch - 16, f.stem)
        c.setStrokeColorRGB(0.18, 0.21, 0.30); c.setLineWidth(0.5)
        c.rect(x0+4, y0+4, cw-8, ch-8, stroke=1, fill=0)
    c.save()
    png = OUT / f"{name}.png"
    subprocess.run(["sips", "-s", "format", "png", str(pdf), "--out", str(png)],
                   capture_output=True)
    print(f"{png}  ({len(files[:cols*rows])} figures)")

if __name__ == "__main__":
    pat, name, cols, rows = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    cell = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (560, 400)
    import os
    files = sorted((HERE/"svg").glob(f"{pat}*.svg"))
    skip = int(os.environ.get("SKIP", "0"))
    files = files[skip:]
    sheet(files, name, cols, rows, cell)
