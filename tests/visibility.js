// Check that everything the app hides via the `hidden` attribute actually
// computes to display:none, and is visible again when shown.
const { JSDOM } = require('jsdom');
const BASE = process.env.BASE || 'http://127.0.0.1:5057';

(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/',
    runScripts: 'dangerously',
    resources: 'usable',
    pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
    },
  });
  const { window } = dom;
  const doc = window.document;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) {
    if (doc.querySelector('.detail-title h2')) break;
    await wait(500);
  }

  const disp = sel => window.getComputedStyle(doc.querySelector(sel)).display;
  const out = {};

  // As delivered, both overlays carry [hidden].
  out['modal @load'] = { hidden: doc.querySelector('#modal').hidden, display: disp('#modal') };
  out['results @load'] = { hidden: doc.querySelector('#results').hidden, display: disp('#results') };

  // Open the modal, then close it with the X.
  doc.getElementById('btn-pathogens').click();
  await wait(1200);
  out['modal open'] = { hidden: doc.querySelector('#modal').hidden, display: disp('#modal') };
  doc.querySelector('#modal [data-close]').click();
  await wait(200);
  out['modal after close btn'] = { hidden: doc.querySelector('#modal').hidden, display: disp('#modal') };

  // Reopen and close by clicking the backdrop.
  doc.getElementById('btn-pathogens').click();
  await wait(900);
  doc.querySelector('#modal').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  await wait(200);
  out['modal after backdrop'] = { hidden: doc.querySelector('#modal').hidden, display: disp('#modal') };

  // Reopen and close with Escape.
  doc.getElementById('btn-pathogens').click();
  await wait(900);
  doc.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  await wait(200);
  out['modal after Escape'] = { hidden: doc.querySelector('#modal').hidden, display: disp('#modal') };

  // Search dropdown: open on input, close on outside click.
  const q = doc.getElementById('q');
  q.value = 'oropouche';
  q.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(900);
  out['results open'] = {
    hidden: doc.querySelector('#results').hidden,
    display: disp('#results'),
    n: doc.querySelectorAll('.result').length,
  };
  doc.body.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  await wait(200);
  out['results after outside click'] = {
    hidden: doc.querySelector('#results').hidden, display: disp('#results'),
  };

  const fails = Object.entries(out).filter(([k, v]) =>
    (v.hidden === true && v.display !== 'none') ||
    (v.hidden === false && v.display === 'none'));

  console.log(JSON.stringify(out, null, 1));
  console.log(fails.length ? '\nFAIL: ' + fails.map(f => f[0]).join(', ') : '\nPASS: hidden state matches computed display everywhere');
  window.close();
  process.exit(fails.length ? 1 : 0);
})();
