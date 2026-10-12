// Drive the radial taxonomy tree end to end.
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
      // jsdom has no layout; d3.zoom needs these.
      w.SVGElement.prototype.getScreenCTM = function () {
        return { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0, inverse() { return this; },
                 multiply() { return this; } };
      };
      w.SVGElement.prototype.createSVGPoint = function () {
        return { x: 0, y: 0, matrixTransform() { return { x: 0, y: 0 }; } };
      };
      // d3-interpolate parses SVG transforms through transform.baseVal, which
      // jsdom does not implement. Returning null makes d3 fall back to its
      // identity transform: no smooth tween, but the final attribute value is
      // still written, which is what these assertions check.
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
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) { if (q('.hero h2')) break; await wait(500); }

  const report = {};
  report.d3 = typeof window.d3 !== 'undefined' ? window.d3.version : 'MISSING';
  report.radialModule = typeof window.Radial;

  // Open the radial view from the toolbar.
  q('#btn-radial').click();
  for (let i = 0; i < 50; i++) { if (q('.rad-node')) break; await wait(400); }
  await wait(1400);

  const snap = () => ({
    hub: q('.rad-hub-name')?.textContent,
    hubSub: q('.rad-hub-sub')?.textContent,
    nodes: doc.querySelectorAll('.rad-node').length,
    links: doc.querySelectorAll('.rad-link').length,
    labels: doc.querySelectorAll('.rad-lab').length,
    rings: doc.querySelectorAll('.rad-ring').length,
    ringLabels: [...doc.querySelectorAll('.rad-ring-lab')].map(t => t.textContent),
    stat: q('.rad-stat')?.textContent,
    crumbs: [...doc.querySelectorAll('.rad-crumbs button')].map(b => b.textContent),
  });

  report.opened = snap();
  report.panelVisible = !q('#radial-panel').hidden;
  report.layoutClass = q('.layout').className;

  // Every node must have a real transform, and no NaN anywhere.
  const transforms = [...doc.querySelectorAll('.rad-node')].map(n => n.getAttribute('transform'));
  report.transformsOk = transforms.every(t => t && !/NaN|undefined/.test(t));
  const paths = [...doc.querySelectorAll('.rad-link')].map(p => p.getAttribute('d') || '');
  report.linkPathsOk = paths.every(d => d.length > 8 && !/NaN|undefined/.test(d));
  report.sampleTransform = transforms[1];
  report.samplePath = paths[0]?.slice(0, 60);

  // Hovering a node should trace its lineage back to the hub.
  const target = [...doc.querySelectorAll('.rad-dot')][4];
  target.dispatchEvent(new window.MouseEvent('mouseover', { bubbles: true }));
  await wait(300);
  report.hover = {
    hasHoverClass: q('.radial').classList.contains('has-hover'),
    litNodes: doc.querySelectorAll('.rad-node.lit').length,
    litLinks: doc.querySelectorAll('.rad-link.lit').length,
    tipVisible: !q('.rad-tip').hidden,
    tipText: q('.rad-tip')?.textContent.replace(/\s+/g, ' ').trim().slice(0, 80),
  };

  // Click an internal node -> re-root, animate, new hub.
  const before = snap();
  const internal = [...doc.querySelectorAll('.rad-node')]
    .find(n => !n.classList.contains('is-root') &&
               ['serogroup', 'genus', 'family', 'clade'].includes(n.dataset.rank));
  report.rerootFrom = before.hub;
  report.rerootRank = internal?.dataset.rank;
  internal.querySelector('.rad-dot').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  for (let i = 0; i < 40; i++) {
    if (q('.rad-hub-name')?.textContent !== before.hub) break;
    await wait(300);
  }
  await wait(1200);
  report.afterReroot = snap();

  // Depth control rebuilds the tree.
  const depthSel = q('.rad-depth');
  depthSel.value = '4';
  depthSel.dispatchEvent(new window.Event('change', { bubbles: true }));
  await wait(2500);
  report.depth4 = { nodes: doc.querySelectorAll('.rad-node').length, stat: q('.rad-stat')?.textContent };

  // "up a rank" walks back out.
  q('.rad-up').click();
  await wait(2200);
  report.afterUp = { hub: q('.rad-hub-name')?.textContent, nodes: doc.querySelectorAll('.rad-node').length };

  // Clicking a species tip should open it in the article panel.
  const tip = [...doc.querySelectorAll('.rad-node')].find(n => n.dataset.rank === 'species');
  if (tip) {
    report.tipClicked = tip.querySelector('title')?.textContent?.split(' — ')[0];
    tip.querySelector('.rad-dot').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    await wait(2200);
    report.articleAfterTip = q('.hero h2')?.textContent;
  }

  // Close it again.
  q('#btn-radial-close').click();
  await wait(300);
  report.closed = { hidden: q('#radial-panel').hidden, layout: q('.layout').className };

  console.log(JSON.stringify(report, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
