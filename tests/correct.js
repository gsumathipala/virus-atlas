// Drive the tier correction control through the DOM.
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
      w.SVGElement.prototype.getScreenCTM = () => ({a:1,b:0,c:0,d:1,e:0,f:0,inverse(){return this;},multiply(){return this;}});
      w.SVGElement.prototype.createSVGPoint = () => ({x:0,y:0,matrixTransform(){return {x:0,y:0};}});
      Object.defineProperty(w.SVGElement.prototype,'transform',{configurable:true,
        get(){return {baseVal:{numberOfItems:0,consolidate:()=>null}};}});
      w.addEventListener('error', e => errors.push('error: ' + e.message));
      w.onunhandledrejection = e => errors.push('rejection: ' + (e.reason?.message || e.reason));
      const ce = w.console.error;
      w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); ce(...a); };
    },
  });
  const { window } = dom, doc = window.document, q = s => doc.querySelector(s);
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const click = el => el.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  for (let i = 0; i < 60; i++) { if (q('.hero h2')) break; await wait(500); }

  const R = {};
  // Pick an unassessed species: Betainfluenzavirus is now reference-tier, so use a
  // genuinely unassessed one via search.
  q('#q').value = 'Jeilongvirus ratti';
  q('#q').dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(1400);
  const hit = q('#results button.result');
  R.searchHit = hit?.textContent.trim().slice(0, 40);
  click(hit); await wait(2200);

  R.species = q('.hero h2')?.textContent;
  R.tierBadge = q('.hero .badge[data-tier]')?.getAttribute('data-tier');
  R.provBasis = q('.prov')?.dataset.basis;
  R.provLabel = q('.prov-label')?.textContent;
  R.provWhy = q('.prov-why')?.textContent.slice(0, 90);
  R.synonyms = [...doc.querySelectorAll('.detail-synonyms b')].map(b => b.textContent);

  // Open the editor.
  click(q('[data-correct]')); await wait(300);
  R.editorOpen = !!q('.correct');
  R.tierOptions = [...doc.querySelectorAll('.correct select option')].map(o => o.value);

  // Save a correction.
  q('.correct select').value = 'probable';
  q('.correct input[name=note]').value = 'jsdom test correction';
  q('.correct').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  for (let i = 0; i < 40; i++) { if (q('.prov')?.dataset.basis === 'override') break; await wait(300); }
  await wait(600);
  R.afterSave = {
    basis: q('.prov')?.dataset.basis,
    label: q('.prov-label')?.textContent,
    badge: q('.hero .badge[data-tier]')?.getAttribute('data-tier'),
    note: q('.prov-why')?.textContent,
    was: q('.prov-was')?.textContent.replace(/\s+/g, ' ').trim(),
  };

  // Server really stored it.
  const stored = await (await window.fetch(BASE + '/api/corrections')).json();
  R.storedOnServer = stored.corrections.find(c => c.species === 'Jeilongvirus ratti') || null;

  // Now remove it.
  click(q('[data-correct]')); await wait(300);
  click(q('[data-revert]'));
  for (let i = 0; i < 40; i++) { if (q('.prov')?.dataset.basis !== 'override') break; await wait(300); }
  await wait(600);
  R.afterRevert = { basis: q('.prov')?.dataset.basis, badge: q('.hero .badge[data-tier]')?.getAttribute('data-tier') };
  const after = await (await window.fetch(BASE + '/api/corrections')).json();
  R.remaining = after.corrections.length;

  console.log(JSON.stringify(R, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
