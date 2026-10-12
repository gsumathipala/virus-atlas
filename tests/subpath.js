// The static build served from a SUBPATH, as GitHub Pages does.
//
// Written after the distribution map failed live with "JSON.parse:
// unexpected character at line 1 column 1": the map fetched
// /static/data/world.json against location.origin, which on a subpath
// resolves above the site root and returns the host's HTML 404 page.
// Serving from / hid it completely, which is why every earlier suite passed.
const { JSDOM } = require('jsdom');
const BASE = process.env.BASE || 'http://127.0.0.1:5071/virus-atlas';
const errors = [];
(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/', runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) { w.fetch=(...a)=>fetch(...a); w.Element.prototype.scrollIntoView=function(){};
      w.SVGElement.prototype.getScreenCTM=()=>({a:1,b:0,c:0,d:1,e:0,f:0,inverse(){return this;},multiply(){return this;}});
      w.SVGElement.prototype.createSVGPoint=()=>({x:0,y:0,matrixTransform(){return{x:0,y:0};}});
      Object.defineProperty(w.SVGElement.prototype,'transform',{configurable:true,get(){return{baseVal:{numberOfItems:0,consolidate:()=>null}};}});
      w.addEventListener('error',e=>errors.push('error: '+e.message));
      const ce=w.console.error; w.console.error=(...a)=>{errors.push('console.error: '+a.join(' ')); ce(...a);};
    }});
  const {window}=dom, doc=window.document, q=s=>doc.querySelector(s), all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<80;i++){ if(q('.tree-node')) break; await wait(500); }

  const R = { base: BASE };
  // Pick viruses with a mapped distribution.
  for (const name of ['dengue','Rift Valley fever','Lassa']) {
    q('#q').value = name;
    q('#q').dispatchEvent(new window.Event('input', { bubbles: true }));
    await wait(2200);
    const hit = q('#results button.result');
    if (!hit) { R[name] = 'no search hit'; continue; }
    click(hit);
    for (let i=0;i<50;i++){ if(q('.map-loading')||q('.geo-country, .map-fig, [class*=geo]')) break; await wait(400); }
    await wait(2500);
    const failure = q('.map-loading');
    // The real classes mapFigure emits: every country is path.geo, and the
    // ones in range carry .on. Asserting on both means the test fails if the
    // map silently renders empty, not only if it throws.
    R[name] = {
      species: q('.hero h2')?.textContent,
      mapError: failure ? failure.textContent.trim().slice(0, 80) : null,
      mapSvg: !!q('svg.fig-map'),
      countriesDrawn: all('svg.fig-map path.geo').length,
      countriesHighlighted: all('svg.fig-map path.geo.on').length,
    };
  }
  console.log(JSON.stringify(R, null, 1));
  console.log('\nERRORS:', errors.length ? errors.slice(0,4) : 'none');
  // Fail on a thrown error OR on a map that drew nothing.
  const broke = Object.entries(R).some(([k, v]) =>
    k !== 'base' && v && (v.mapError || !v.mapSvg ||
                          v.countriesDrawn < 100 || v.countriesHighlighted < 1));
  window.close();
  process.exit(broke || errors.length ? 1 : 0);
})();
