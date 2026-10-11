"""Bake a world map into SVG paths for the distribution figures.

Source: Natural Earth 110m country boundaries, via the world-atlas TopoJSON
build. Natural Earth is public domain.

TopoJSON is decoded here rather than in the browser so the client needs no
topojson library -- the output is a flat {country name: SVG path} map in an
equirectangular projection, which is all the figure needs.

Usage:  python build_world.py
"""

import json
import urllib.request
from pathlib import Path

SRC = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json"
OUT = Path(__file__).resolve().parent / "static" / "data" / "world.json"

WIDTH, HEIGHT = 1000.0, 500.0
PRECISION = 1          # decimal places in path output
MIN_RING_AREA = 0.6    # drop specks smaller than this (px^2 of projected area)


def decode_arcs(topo):
    """Delta-decoded, quantised arcs -> absolute [lon, lat] coordinate lists."""
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        points = []
        for dx, dy in arc:
            x += dx
            y += dy
            points.append((x * sx + tx, y * sy + ty))
        arcs.append(points)
    return arcs


def project(lon, lat):
    return ((lon + 180.0) / 360.0 * WIDTH, (90.0 - lat) / 180.0 * HEIGHT)


def ring_points(arc_indices, arcs):
    """Stitch a ring from signed arc indices (negative = traverse reversed)."""
    out = []
    for idx in arc_indices:
        arc = arcs[~idx] if idx < 0 else arcs[idx]
        seq = reversed(arc) if idx < 0 else arc
        for lon, lat in seq:
            p = project(lon, lat)
            if not out or out[-1] != p:
                out.append(p)
    return out


def shoelace(points):
    a = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def to_path(points):
    """Path data, split wherever a ring jumps the antimeridian.

    Equirectangular projection maps lon -180 and +180 to opposite edges, so a
    polygon crossing the dateline (Russia, Fiji, Alaska) would otherwise be
    drawn as a horizontal streak straight across the map.
    """
    f = f".{PRECISION}f"
    d = []
    last = None
    for x, y in points:
        if last is not None:
            same = (round(x, PRECISION) == round(last[0], PRECISION)
                    and round(y, PRECISION) == round(last[1], PRECISION))
            if same:
                continue
            if abs(x - last[0]) > WIDTH / 2:      # dateline jump
                d.append("Z")
                last = None
        d.append(f"{'M' if last is None else 'L'}{x:{f}} {y:{f}}")
        last = (x, y)
    return "".join(d) + "Z" if d else ""


def main():
    print(f"fetching {SRC}")
    with urllib.request.urlopen(SRC, timeout=120) as r:
        topo = json.loads(r.read().decode())

    arcs = decode_arcs(topo)
    countries = {}
    for geom in topo["objects"]["countries"]["geometries"]:
        name = (geom.get("properties") or {}).get("name")
        if not name:
            continue
        polygons = (
            [geom["arcs"]] if geom["type"] == "Polygon" else geom.get("arcs", [])
        )
        parts = []
        centroid_acc, area_acc = [0.0, 0.0], 0.0
        for rings in polygons:
            for ring in rings:
                pts = ring_points(ring, arcs)
                if len(pts) < 4:
                    continue
                area = shoelace(pts)
                if area < MIN_RING_AREA:
                    continue
                parts.append(to_path(pts))
                cx = sum(p[0] for p in pts) / len(pts)
                cy = sum(p[1] for p in pts) / len(pts)
                centroid_acc[0] += cx * area
                centroid_acc[1] += cy * area
                area_acc += area
        if not parts:
            continue
        countries[name] = {
            "d": "".join(parts),
            "c": [round(centroid_acc[0] / area_acc, 1),
                  round(centroid_acc[1] / area_acc, 1)] if area_acc else None,
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "width": WIDTH,
        "height": HEIGHT,
        "projection": "equirectangular",
        "source": "Natural Earth 110m (public domain) via world-atlas",
        "countries": countries,
    }
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT} — {len(countries)} countries, "
          f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
