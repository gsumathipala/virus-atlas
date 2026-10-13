# Tests

Eighteen suites that drive the running application in [jsdom][] and assert on
the resulting DOM, plus the tooling used to look at the SVG the app produces.

There is no browser in the environment this was built in, which shapes
everything here. jsdom gives a real DOM, real CSS cascade and real JavaScript
execution, so behaviour and computed styles can be checked — but it has **no
layout engine**, so nothing here can tell you whether the page looks right at
a given width. That gap is real and is stated in the main README too.

## Running them

```bash
cd tests && npm install          # jsdom only
python ../app.py &               # the suites drive a live server on :5057
node smoke.js                    # ... or any other suite
```

Each exits non-zero if the page logged an error, so they work in a loop:

```bash
for t in smoke visibility isolate live figs radial split \
         correct travel views genomic nav dx dxje; do
  printf '%-11s ' $t; node $t.js >/dev/null 2>&1 && echo PASS || echo FAIL
done
```

### Against the static build

Every suite takes `BASE`, so the same assertions can be run against the copy
GitHub Pages serves rather than against Flask:

```bash
python ../export_static.py
(cd ../site && python -m http.server 5070) &
BASE=http://127.0.0.1:5070 node smoke.js
```

Do run them both ways. The two builds answer the same URLs from entirely
different code, and for a long time only Flask was ever tested: the hosted
copy was quietly serving a trimmed record for every family, no record at all
for 2,611 species, and no isolates, and nothing here noticed.

## What each one covers

| Suite | Covers |
| --- | --- |
| `smoke` | Boot, tree expansion, search, sidebar render, no console errors |
| `visibility` | Computed styles, not just the `hidden` property — written after a modal that `[hidden]` could not close |
| `isolate` | Isolate nodes resolve to their species payload |
| `live` | Europe PMC lookup and its cache |
| `figs` | Every figure type emits valid geometry with no NaN |
| `radial` | Open, re-root, depth change, up-a-rank, hover lineage, tip to article |
| `split` | Top-level split mode: wedge count, real angular gaps, nothing within the hub |
| `correct` | Tier correction round trip, persistence, rollup, revert |
| `travel` | Destination query, route grouping, incubation windows, evidence grades |
| `views` | Exactly one left-column panel visible across every transition |
| `genomic` | Nextstrain build summaries, and absence handled quietly |
| `nav` | Selecting a virus from search, travel, index or signals moves the tree |
| `dx` | Differential panel, virology blocks, syndrome-chip loop |
| `dxje` | Regression: a destination-specific virus must survive country filtering |
| `static` | The static build end to end: tree, search, radial, travel, differential, index |
| `subpath` | The static build served from `/virus-atlas/`, as Pages serves it |
| `parity` | Static and Flask answer the same JSON, field by field |
| `cycle` | Every transmission figure draws how *people* are infected — not an evolutionary origin |

`cycle` needs no server at all: it loads `figures.js` directly and renders
every profile, so it runs in a second and is the cheapest check in here.

`parity` is the one that needs both servers up at once — Flask on :5057 and
the static build on :5070 — because it asks each the same questions and diffs
the answers. Only a cache's age and state are allowed to differ, along with
the ECDC link, which cannot be fetched from a browser at all because
ecdc.europa.eu sends no CORS header.

## Tools

`tools/` holds the visual-QA pipeline. `emit_docs.js` renders the app's SVG
from a live page; `rasterize.py` inlines the stylesheet (svglib honours
presentation attributes but not external CSS, custom properties or
`color-mix()`) and `render_docs.py` turns the result into the PNGs in
`docs/img`.

This pipeline exists because structural assertions missed five real defects
that were obvious the moment the figures were actually looked at: spikes drawn
inside a particle, a filament rendered as a thin arc, labels over artwork, map
geometry streaking across the antimeridian, and an icon that read as a spider
rather than a sloth.

[jsdom]: https://github.com/jsdom/jsdom
