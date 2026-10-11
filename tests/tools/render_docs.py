"""Render the emitted app SVG to PNG for the repository docs.

Reuses rasterize.py's CSS inliner (svglib ignores external stylesheets,
custom properties and color-mix), renders each drawing to its own
tightly-sized PDF, then converts with macOS `sips`. These are the app's own
vector output at high resolution -- not browser screenshots, which this
environment cannot produce.
"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rasterize as R
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas as rl_canvas

SRC = Path(__file__).resolve().parent / "docsvg"
DST = Path("/Users/saranga/virus-atlas/docs/img")
DST.mkdir(parents=True, exist_ok=True)
SCALE = 2.0                                  # retina-ish
BG = (0.051, 0.059, 0.078)

rules = R.parse_rules(R.CSS.read_text(), R.parse_root_vars(R.CSS.read_text()))
for f in sorted(SRC.glob("*.svg")):
    try:
        styled = SRC / (f.stem + ".styled.svg")
        styled.write_text(R.apply_css(f.read_text(), rules))
        d = svg2rlg(str(styled))
        styled.unlink()
        if d is None or not d.width:
            print(f"  {f.stem}: svglib returned nothing"); continue
        w, h = d.width * SCALE, d.height * SCALE
        pdf = DST / (f.stem + ".pdf")
        c = rl_canvas.Canvas(str(pdf), pagesize=(w, h))
        c.setFillColorRGB(*BG); c.rect(0, 0, w, h, stroke=0, fill=1)
        d.scale(SCALE, SCALE); d.width, d.height = w, h
        renderPDF.draw(d, c, 0, 0)
        c.save()
        png = DST / (f.stem + ".png")
        subprocess.run(["sips", "-s", "format", "png", str(pdf),
                        "--out", str(png)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf.unlink()
        print(f"  {f.stem:<28} {int(w)}x{int(h)}  {png.stat().st_size//1024} KB")
    except Exception as e:
        print(f"  {f.stem}: FAILED {type(e).__name__}: {e}")
