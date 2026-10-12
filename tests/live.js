// Exercise the live-evidence panel in the sidebar.
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
  const q = s => doc.querySelector(s);
  for (let i = 0; i < 60; i++) { if (doc.querySelector('.hero h2')) break; await wait(500); }

  const report = {};
  const settle = async () => {
    for (let i = 0; i < 40; i++) {
      const s = q('.live .live-status');
      if (!s || !/Searching|Refreshing/.test(s.textContent)) break;
      await wait(500);
    }
  };

  // --- profiled species (the seed: Oya)
  await settle();
  report.seed = {
    title: q('.hero h2').textContent,
    liveSectionPresent: !!q('.live'),
    summary: q('.live-summary')?.textContent.replace(/\s+/g, ' ').trim(),
    papers: doc.querySelectorAll('.paper').length,
    humanFlags: doc.querySelectorAll('.flag-human').length,
    titleFocus: doc.querySelectorAll('.paper[data-focus="title"]').length,
    aiCardClass: q('.ai-card')?.className || 'removed',
    aiOffText: 'n/a',
    firstPaper: q('.paper-title')?.textContent.slice(0, 70),
    firstPaperLinks: [...doc.querySelectorAll('.paper .ref-links a')].slice(0, 3).map(a => a.textContent),
    abstractToggles: doc.querySelectorAll('.paper-abs').length,
    foot: q('.live-foot')?.textContent.replace(/\s+/g, ' ').trim().slice(0, 60),
  };

  // --- an UNPROFILED species: this is the case the lookup exists for
  const input = q('#q');
  input.value = 'Orthobunyavirus nolaense';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(1000);
  q('.result').click();
  await wait(1200);
  await settle();
  report.unprofiled = {
    title: q('.hero h2').textContent,
    sections: [...doc.querySelectorAll('.section > h3')].map(h => h.textContent.trim().split('\n')[0]),
    noProfileNote: q('.section p')?.textContent.replace(/\s+/g, ' ').trim().slice(0, 80),
    summary: q('.live-summary')?.textContent.replace(/\s+/g, ' ').trim(),
    papers: doc.querySelectorAll('.paper').length,
    humanFlags: doc.querySelectorAll('.flag-human').length,
    weakFlags: doc.querySelectorAll('.flag-weak').length,
  };

  // --- a non-vertebrate virus should show no human flags at all
  input.value = 'Wargodvirus xiongnu';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(1000);
  q('.result').click();
  await wait(1200);
  await settle();
  report.archaeal = {
    title: q('.hero h2').textContent,
    summary: q('.live-summary')?.textContent.replace(/\s+/g, ' ').trim(),
    humanFlags: doc.querySelectorAll('.flag-human').length,
  };

  // --- refresh button re-fetches in place
  q('.live-foot [data-retry]').click();
  await wait(600);
  report.refreshShowsStatus = /Refreshing/.test(q('.live .live-status')?.textContent || '');
  await settle();
  report.afterRefreshPapers = doc.querySelectorAll('.paper').length;

  // --- isolate view also gets the live panel (via its parent species)
  const spRow = q('.tree-row.selected');
  report.liveOnIsolate = 'n/a';
  if (spRow) {
    spRow.click(); await wait(1200);
    const iso = [...doc.querySelectorAll('.tree-row[data-rank="isolate"]')][0];
    if (iso) {
      iso.click(); await wait(1200); await settle();
      report.liveOnIsolate = { title: q('.hero h2').textContent, live: !!q('.live'),
                               papers: doc.querySelectorAll('.paper').length };
    }
  }

  console.log(JSON.stringify(report, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
