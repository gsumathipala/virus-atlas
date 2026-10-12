// Split mode: at "All viruses" the lineages must be drawn apart, with no link
// reaching the centre, and re-rooting into a realm must reconnect normally.
const { JSDOM } = require('jsdom');
const BASE = process.env.BASE || 'http://127.0.0.1:5057';
const errors = [];

(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/', runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
      w.SVGElement.prototype.getScreenCTM = () => ({ a:1,b:0,c:0,d:1,e:0,f:0, inverse(){return this;}, multiply(){return this;} });
      w.SVGElement.prototype.createSVGPoint = () => ({ x:0,y:0, matrixTransform(){return {x:0,y:0};} });
      Object.defineProperty(w.SVGElement.prototype, 'transform', {
        configurable: true,
        get() { return { baseVal: { numberOfItems: 0, consolidate: () => null } }; },
      });
      w.addEventListener('error', e => errors.push('error: ' + e.message));
      w.onunhandledrejection = e => errors.push('rejection: ' + (e.reason?.message || e.reason));
      const ce = w.console.error;
      w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); ce(...a); };
    },
  });
  const { window } = dom, doc = window.document, q = s => doc.querySelector(s);
  const all = s => [...doc.querySelectorAll(s)];
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) { if (q('.hero h2')) break; await wait(500); }

  q('#btn-radial').click();
  for (let i = 0; i < 50; i++) { if (q('.rad-node')) break; await wait(400); }
  await wait(1200);

  // Jump to the top of the tree via the first breadcrumb.
  const first = all('.rad-crumbs button')[0];
  first.click();
  for (let i = 0; i < 40; i++) { if (q('.radial').classList.contains('is-split')) break; await wait(300); }
  await wait(1600);

  const R = {};
  R.splitClass = q('.radial').classList.contains('is-split');
  R.hub = q('.rad-hub-name')?.textContent;
  R.hubSub = q('.rad-hub-sub')?.textContent;
  R.stat = q('.rad-stat')?.textContent;

  // No root node drawn, and no link may start at radius 0.
  R.rootNodes = all('.rad-node.is-root').length;
  R.lineageNodes = all('.rad-node.is-lineage').length;
  const d1 = all('.rad-node.is-lineage').map(n => n.getAttribute('transform'));
  const radiusOf = t => +(/translate\(([-\d.]+)/.exec(t || '')?.[1] ?? NaN);
  R.lineageRadii = [...new Set(d1.map(t => radiusOf(t).toFixed(1)))];

  // Every link must live entirely outside the inner hole.
  const paths = all('.rad-link').map(p => p.getAttribute('d') || '');
  const nums = d => (d.match(/-?\d+\.?\d*/g) || []).map(Number);
  let minDist = Infinity;
  for (const d of paths) {
    const v = nums(d);
    for (let i = 0; i + 1 < v.length; i += 2) minDist = Math.min(minDist, Math.hypot(v[i], v[i + 1]));
  }
  R.minLinkDistanceFromCentre = Math.round(minDist);
  R.allLinksOutsideHole = minDist > 60;
  R.linkPathsOk = paths.every(d => d.length > 8 && !/NaN|undefined/.test(d));

  // Brackets: one per lineage, with real gaps between consecutive wedges.
  const arcs = all('.rad-arc');
  R.brackets = arcs.length;
  R.bracketsLabelled = all('.rad-arc textPath').filter(t => t.textContent.trim()).length;
  R.sampleBracketLabels = all('.rad-arc textPath').map(t => t.textContent.trim()).filter(Boolean).slice(0, 6);
  R.bracketPathsOk = all('.rad-arc-band').every(p => {
    const d = p.getAttribute('d') || '';
    return /^M[-\d.]+,[-\d.]+A/.test(d) && !/NaN/.test(d);
  });

  // Gaps: compute each wedge's angular extent from its band endpoints.
  const ang = (x, y) => (Math.atan2(x, -y) + 2 * Math.PI) % (2 * Math.PI);
  const spans = all('.rad-arc-band').map(p => {
    const v = nums(p.getAttribute('d'));
    const a = ang(v[0], v[1]), b = ang(v[v.length - 2], v[v.length - 1]);
    return [Math.min(a, b), Math.max(a, b)];
  }).sort((p, r) => p[0] - r[0]);
  let gaps = [];
  for (let i = 1; i < spans.length; i++) gaps.push(spans[i][0] - spans[i - 1][1]);
  R.wedgeCount = spans.length;
  R.minGapDegrees = +(Math.min(...gaps) * 180 / Math.PI).toFixed(2);
  R.everyWedgeSeparated = gaps.every(g => g > 0.004);
  R.widestWedge = (() => {
    let best = 0, bi = 0;
    spans.forEach((s, i) => { if (s[1] - s[0] > best) { best = s[1] - s[0]; bi = i; } });
    return `${(best * 180 / Math.PI).toFixed(1)}deg`;
  })();

  // Hovering a bracket should light that lineage.
  all('.rad-arc-band')[0].dispatchEvent(new window.MouseEvent('mouseover', { bubbles: true }));
  await wait(300);
  R.bracketHover = { lit: all('.lit').length, tip: q('.rad-tip')?.textContent.replace(/\s+/g,' ').trim().slice(0,60) };

  // Clicking a bracket re-roots into that realm, which must reconnect.
  all('.rad-arc-band')[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  for (let i = 0; i < 40; i++) { if (!q('.radial').classList.contains('is-split')) break; await wait(300); }
  await wait(1500);
  R.afterRerootIntoRealm = {
    split: q('.radial').classList.contains('is-split'),
    hub: q('.rad-hub-name')?.textContent,
    brackets: all('.rad-arc').length,
    rootNodes: all('.rad-node.is-root').length,
    nodes: all('.rad-node').length,
  };

  console.log(JSON.stringify(R, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
