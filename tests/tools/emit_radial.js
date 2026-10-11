// Render the radial tree in jsdom and dump the finished SVG for rasterising.
// jsdom has no SVGTransformList, so d3's transform interpolation is given a
// real matrix implementation here; without it every node lands on the origin.
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');
const BASE = 'http://127.0.0.1:5057';
const OUT = path.join(__dirname, 'svg');

function matrixFrom(str) {
  let m = [1, 0, 0, 1, 0, 0];                         // a b c d e f
  const mul = (x, y) => [
    x[0] * y[0] + x[2] * y[1], x[1] * y[0] + x[3] * y[1],
    x[0] * y[2] + x[2] * y[3], x[1] * y[2] + x[3] * y[3],
    x[0] * y[4] + x[2] * y[5] + x[4], x[1] * y[4] + x[3] * y[5] + x[5],
  ];
  for (const op of String(str || '').matchAll(/(\w+)\s*\(([^)]*)\)/g)) {
    const n = op[2].split(/[\s,]+/).filter(Boolean).map(Number);
    if (op[1] === 'translate') m = mul(m, [1, 0, 0, 1, n[0] || 0, n[1] || 0]);
    else if (op[1] === 'rotate') {
      const r = (n[0] || 0) * Math.PI / 180;
      m = mul(m, [Math.cos(r), Math.sin(r), -Math.sin(r), Math.cos(r), 0, 0]);
    } else if (op[1] === 'scale') m = mul(m, [n[0] ?? 1, 0, 0, n[1] ?? n[0] ?? 1, 0, 0]);
  }
  return { a: m[0], b: m[1], c: m[2], d: m[3], e: m[4], f: m[5] };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/', runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
      w.SVGElement.prototype.getScreenCTM = function () {
        return { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0, inverse() { return this; }, multiply() { return this; } };
      };
      w.SVGElement.prototype.createSVGPoint = function () {
        return { x: 0, y: 0, matrixTransform() { return { x: 0, y: 0 }; } };
      };
      Object.defineProperty(w.SVGElement.prototype, 'transform', {
        configurable: true,
        get() {
          const self = this;
          return { baseVal: {
            numberOfItems: 1,
            consolidate() { return { matrix: matrixFrom(self.getAttribute('transform')) }; },
          } };
        },
      });
    },
  });
  const { window } = dom, doc = window.document, q = s => doc.querySelector(s);
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) { if (q('.hero h2')) break; await wait(500); }

  q('#btn-radial').click();
  for (let i = 0; i < 50; i++) { if (q('.rad-node')) break; await wait(400); }
  await wait(2500);

  const dump = name => {
    const svg = q('.rad-svg').cloneNode(true);
    svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    svg.setAttribute('width', '1000');
    svg.setAttribute('height', '1000');
    fs.writeFileSync(path.join(OUT, `${name}.svg`), svg.outerHTML);
    const t = [...svg.querySelectorAll('.rad-node')].map(n => n.getAttribute('transform'));
    console.log(name, '| nodes', t.length, '| sample', t[2]);
  };

  dump('radial-genus');

  // Re-root on a serogroup, then on the whole family, for two more views.
  const sg = [...doc.querySelectorAll('.rad-node')]
    .find(n => !n.classList.contains('is-root') && n.dataset.rank === 'serogroup');
  sg.querySelector('.rad-dot').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  await wait(2600);
  dump('radial-serogroup');

  q('.rad-up').click(); await wait(2200);
  q('.rad-up').click(); await wait(2600);
  dump('radial-family');

  // And a big one: a whole realm at shallow depth.
  const depthSel = q('.rad-depth'); depthSel.value = '3';
  depthSel.dispatchEvent(new window.Event('change', { bubbles: true }));
  await wait(1500);
  const crumb = [...doc.querySelectorAll('.rad-crumbs button')].find(b => b.textContent === 'Riboviria');
  if (crumb) { crumb.click(); await wait(3200); dump('radial-realm'); }

  window.close();
})();
