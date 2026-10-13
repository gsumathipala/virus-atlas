// Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
// Proprietary. No licence granted; see LICENSE.
//
// The hosted copy must answer what the server answers.
//
// It did not. The static build kept two records for every family -- a
// trimmed tree row in the skeleton and the full one in its bundle -- and the
// browser preferred the trimmed one, so Ampullaviridae lost its bottle-shaped
// virion, every group lost its roster of pathogenic species, and the contents
// list was handed bare id strings. 2,611 species in the family-less
// Caudoviricetes lineages were in no file at all and answered "not found",
// and all 19,285 isolates were missing from the tree.
//
// Nothing caught it because no test ever compared the two. This does: it
// drives the static build in jsdom, calls Flask directly, and diffs the JSON.
//
//   python ../app.py &                       # :5057
//   python ../export_static.py && (cd ../site && python -m http.server 5070)
//   node parity.js
//
const { JSDOM } = require('jsdom');
const STATIC = process.env.BASE || 'http://127.0.0.1:5070';
const FLASK = process.env.FLASK || 'http://127.0.0.1:5057';

// Ranks differ in shape, so cover every one of them, plus the three cases
// that were broken: a family, a family-less genus and its species, an isolate.
const F = 'root/riboviria/orthornavirae/kitrinoviricota/flasuviricetes/amarillovirales/flaviviridae';
const DENV = `${F}/orthoflavivirus/mosquito-borne-dengue-serocomplex/euflavivirus/orthoflavivirus-denguei`;
const CAUDO = 'root/duplodnaviria/heunggongvirae/uroviricota/caudoviricetes';
const NODES = [
  'root',
  'root/ampullaviridae',                       // the one that was reported
  'root/riboviria',
  'root/riboviria/orthornavirae/negarnaviricota',
  F,
  `${F}/orthoflavivirus`,
  `${F}/orthoflavivirus/mosquito-borne-dengue-serocomplex`,
  DENV,
  `${DENV}/i0`,                                // an isolate
  `${CAUDO}/skatevirus`,                       // genus ICTV assigns no family
  `${CAUDO}/fibralongavirus`,
];
const URLS = [
  '/api/subtree?id=root&depth=3&fan=36',
  `/api/subtree?id=${F}&depth=3&fan=12`,
  '/api/search?q=dengue',
  '/api/search?q=ampulla',
  '/api/pathogens',
  '/api/travel?country=Sri%20Lanka&days=11',
  '/api/differential?syndrome=encephalitis&country=Sri%20Lanka',
  '/api/corrections',
];

// What is allowed to differ: a cache's age and state, and the flag that says
// which build this is. Everything else is a failure.
//
// /api/travel carries the WHO and UKHSA reporting for the destination, so
// that one comparison needs both sides to reach the network. The server
// caches for an hour and the page does not, so a report published between
// the two calls will show up here as a difference; re-run before believing
// it.
const EXEMPT = [
  // Cache state: how many lookups each build happens to have cached, and how
  // old they are. The static build's figures are a snapshot of whatever the
  // machine that exported it had cached; the server's keep moving.
  /^\.live\.(cache|surveillance)\./,
  /\.age_s$/, /\.fetched_at$/, /\.(signal_)?sources\[\d+\]\.state$/,
  // Which build this is, and when it was exported. The static copy is a
  // snapshot and says so in its footer; the server is not one.
  /^\.static$/, /^\.generated$/, /^\.source\.snapshot$/, /^\.ecdc$/,
];

function diff(a, b, path = '') {
  if (EXEMPT.some(rx => rx.test(path))) return [];
  const out = [];
  const obj = v => v && typeof v === 'object' && !Array.isArray(v);
  if (obj(a) && obj(b)) {
    for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
      const at = `${path}.${k}`;
      if (EXEMPT.some(rx => rx.test(at))) continue;
      if (!(k in a)) out.push(`${at}: missing from the static build`);
      else if (!(k in b)) out.push(`${at}: only in the static build`);
      else out.push(...diff(a[k], b[k], at));
    }
  } else if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) out.push(`${path}: ${a.length} entries, server sent ${b.length}`);
    a.slice(0, b.length).forEach((x, i) => out.push(...diff(x, b[i], `${path}[${i}]`)));
  } else if (JSON.stringify(a) !== JSON.stringify(b)) {
    out.push(`${path}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
  }
  return out;
}

(async () => {
  const html = await (await fetch(STATIC + '/')).text();
  const dom = new JSDOM(html, {
    url: STATIC + '/', runScripts: 'dangerously', resources: 'usable',
    pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
      w.SVGElement.prototype.getScreenCTM = () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0, inverse() { return this; }, multiply() { return this; } });
      w.SVGElement.prototype.createSVGPoint = () => ({ x: 0, y: 0, matrixTransform() { return { x: 0, y: 0 }; } });
      Object.defineProperty(w.SVGElement.prototype, 'transform', { configurable: true, get() { return { baseVal: { numberOfItems: 0, consolidate: () => null } }; } });
    },
  });
  const w = dom.window;
  for (let i = 0; i < 80; i++) {
    if (w.document.querySelector('.tree-node')) break;
    await new Promise(r => setTimeout(r, 400));
  }
  if (!w.document.querySelector('.tree-node')) {
    console.error('the static build never drew a tree'); process.exit(1);
  }

  const urls = [...URLS, '/api/meta'];
  for (const id of NODES) {
    urls.push(`/api/node?id=${encodeURIComponent(id)}`,
              `/api/children?id=${encodeURIComponent(id)}`);
  }

  let failed = 0;
  for (const u of urls) {
    let ds;
    try {
      const [s, f] = await Promise.all([
        (await w.fetch(u)).json(), (await fetch(FLASK + u)).json(),
      ]);
      ds = diff(s, f);
    } catch (e) {
      ds = [`request failed: ${e.message}`];
    }
    const label = u.length > 72 ? u.slice(0, 40) + '…' + u.slice(-30) : u;
    if (ds.length) {
      failed++;
      console.log(`FAIL ${label}`);
      for (const d of ds.slice(0, 6)) console.log(`       ${d}`);
      if (ds.length > 6) console.log(`       … and ${ds.length - 6} more`);
    } else {
      console.log(`ok   ${label}`);
    }
  }
  console.log(`\n${urls.length} endpoints compared, ${failed} differing`);
  w.close();
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
