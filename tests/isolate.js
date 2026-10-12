// Expand the Oya species in the tree and click the "Oya virus" isolate row.
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
      w.addEventListener('error', e => errors.push('error: ' + e.message));
      w.onunhandledrejection = e => errors.push('rejection: ' + (e.reason?.message || e.reason));
      const ce = w.console.error;
      w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); ce(...a); };
    },
  });
  const { window } = dom, doc = window.document;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) { if (doc.querySelector('.hero h2')) break; await wait(500); }

  // The seed selection already expanded down to the species; its isolate rows
  // appear once the species node itself is open.
  const spRow = doc.querySelector('.tree-row.selected');
  spRow.click();
  await wait(1500);

  const isoRows = [...doc.querySelectorAll('.tree-row[data-rank="isolate"]')];
  const report = {};
  report.isolateRowsInTree = isoRows.map(r => r.textContent.replace(/\s+/g, ' ').trim());
  report.isolateDotTiers = isoRows.map(r => r.querySelector('.dot').dataset.tier);

  const oya = isoRows.find(r => r.textContent.includes('Oya virus'));
  report.foundOyaRow = !!oya;
  oya.click();
  await wait(1800);

  const q = s => doc.querySelector(s);
  report.title = q('.hero h2')?.textContent;
  report.subtitle = q('.detail-common')?.textContent;
  report.badges = [...doc.querySelectorAll('.detail-head .badge')].map(b => b.textContent.trim());
  report.tierNote = q('.tier-note')?.textContent.replace(/\s+/g, ' ').trim().slice(0, 120);
  report.headline = q('.headline')?.textContent.slice(0, 80);
  report.sections = [...doc.querySelectorAll('.section > h3')].map(h => h.textContent);
  report.accessionLinks = [...doc.querySelectorAll('.fact a')].map(a => a.textContent);
  report.segLabels = [...doc.querySelectorAll('.seg')].map(s => s.textContent);
  report.evidenceItems = doc.querySelectorAll('.evidence li').length;
  report.refItems = doc.querySelectorAll('.ref').length;
  report.panelTextLength = q('.detail').textContent.replace(/\s+/g, ' ').trim().length;

  // The "species this isolate belongs to" link should navigate.
  q('.tier-note .link').click();
  await wait(1500);
  report.afterSpeciesLink = q('.hero h2')?.textContent;

  console.log(JSON.stringify(report, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
