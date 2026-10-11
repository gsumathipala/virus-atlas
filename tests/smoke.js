// Drive the Virus Atlas client in jsdom against the live Flask app.
const { JSDOM } = require('jsdom');

const BASE = 'http://127.0.0.1:5057';
const errors = [];

(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/',
    runScripts: 'dangerously',
    resources: 'usable',
    pretendToBeVisual: true,
    beforeParse(window) {
      window.fetch = (...a) => fetch(...a);
      // jsdom implements neither of these; browsers do.
      window.Element.prototype.scrollIntoView = function () {};
      window.localStorage.clear?.();
      window.addEventListener('error', e => errors.push('window error: ' + e.message));
      window.onunhandledrejection = e => errors.push('rejection: ' + (e.reason?.message || e.reason));
      const origErr = window.console.error;
      window.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); origErr(...a); };
    },
  });

  const { window } = dom;
  const doc = window.document;
  const wait = ms => new Promise(r => setTimeout(r, ms));

  // The inline <script src> is fetched by jsdom's resource loader; give it time
  // plus the boot() round-trips to /api/meta and /api/node.
  for (let i = 0; i < 60; i++) {
    if (doc.querySelector('.hero h2')) break;
    await wait(500);
  }

  const q = s => doc.querySelector(s);
  const report = {};

  report.treeRealms = doc.querySelectorAll('#tree > .tree-node').length;
  report.treeSub = q('#tree-sub')?.textContent.trim();
  report.legendItems = doc.querySelectorAll('#legend .legend-item').length;
  report.seedTitle = q('.hero h2')?.textContent;
  report.seedCommon = q('.detail-common')?.textContent;
  report.seedBadges = [...doc.querySelectorAll('.detail-head .badge')].map(b => b.textContent.trim());
  report.sectionHeads = [...doc.querySelectorAll('.section > h3')].map(h => h.textContent);
  report.evidenceItems = doc.querySelectorAll('.evidence li').length;
  report.refItems = doc.querySelectorAll('.ref').length;
  report.refLinks = [...doc.querySelectorAll('.ref-links a')].slice(0, 3).map(a => a.href);
  report.isolateRows = doc.querySelectorAll('.iso-table tbody tr').length;
  report.seedRevealed = !!q('.tree-row.selected');
  report.selectedName = q('.tree-row.selected .tree-name')?.textContent;
  report.manzanillaOpen = !![...doc.querySelectorAll('.tree-row')]
    .find(r => r.textContent.includes('Manzanilla clade'));

  // --- breadcrumb navigation: click the genus crumb -> group view
  const genusCrumb = [...doc.querySelectorAll('.crumbs button')]
    .find(b => b.textContent === 'Orthobunyavirus');
  genusCrumb.click();
  await wait(1200);
  report.genusTitle = q('.hero h2')?.textContent;
  report.genusDistKeys = doc.querySelectorAll('.dist-key').length;
  report.genusSections = [...doc.querySelectorAll('.section > h3')].map(h => h.textContent);
  report.highlightRows = doc.querySelectorAll('.rows .row-btn').length;

  // --- search flow
  const input = q('#q');
  input.value = 'OYAV';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(900);
  report.searchResults = [...doc.querySelectorAll('.result')].map(r =>
    r.querySelector('.result-name').textContent + ' [' + r.querySelector('.result-rank').textContent + ']');
  report.searchHighlightedEm = q('.result-name em')?.textContent;

  doc.querySelector('.result').click();
  await wait(1200);
  report.afterSearchTitle = q('.hero h2')?.textContent;

  // --- pathogen index modal
  q('#btn-pathogens').click();
  await wait(1200);
  report.modalHidden = q('#modal').hidden;
  report.modalTierBlocks = [...doc.querySelectorAll('.tier-block header h3')].map(h => h.textContent);
  report.modalEntries = doc.querySelectorAll('.tier-grid .row-btn').length;
  const first = q('.tier-grid .row-btn');
  report.modalFirstEntry = first?.textContent.replace(/\s+/g, ' ').trim().slice(0, 70);
  first.click();
  await wait(1200);
  report.modalClosedAfterPick = q('#modal').hidden;
  report.afterModalTitle = q('.hero h2')?.textContent;

  // --- theme toggle
  q('#btn-theme').click();
  report.theme = doc.documentElement.dataset.theme;

  // --- a no-profile species still renders
  const r2 = await (await fetch(BASE + '/api/search?q=Shoyavirus%20shoya')).json();
  input.value = 'Shoyavirus shoya';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(900);
  doc.querySelector('.result').click();
  await wait(1500);
  report.unprofiledTitle = q('.hero h2')?.textContent;
  report.unprofiledSections = [...doc.querySelectorAll('.section > h3')].map(h => h.textContent);

  console.log(JSON.stringify(report, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
