// Drive the STATIC build: no Flask, every /api call answered by the shim.
const { JSDOM } = require('jsdom');
const BASE='http://127.0.0.1:5070'; const errors=[];
(async()=>{
  const html=await (await fetch(BASE+'/')).text();
  const dom=new JSDOM(html,{url:BASE+'/',runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,
    beforeParse(w){w.fetch=(...a)=>fetch(...a);w.Element.prototype.scrollIntoView=function(){};
      w.SVGElement.prototype.getScreenCTM=()=>({a:1,b:0,c:0,d:1,e:0,f:0,inverse(){return this;},multiply(){return this;}});
      w.SVGElement.prototype.createSVGPoint=()=>({x:0,y:0,matrixTransform(){return{x:0,y:0};}});
      Object.defineProperty(w.SVGElement.prototype,'transform',{configurable:true,get(){return{baseVal:{numberOfItems:0,consolidate:()=>null}};}});
      w.addEventListener('error',e=>errors.push('error: '+e.message));
      w.onunhandledrejection=e=>errors.push('rejection: '+(e.reason?.message||e.reason));
      const ce=w.console.error;w.console.error=(...a)=>{errors.push('console.error: '+a.join(' '));ce(...a);};
    }});
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<80;i++){if(q('.hero h2')||q('.tree-node'))break;await wait(500);}
  const R={};
  R.treeRows = all('.tree-node').length;
  R.legend = !!q('#legend .dist-key, #legend span');

  // search -> open a species
  q('#q').value='Oya virus'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(2500);
  R.searchHits = all('#results button.result').length;
  R.firstHit = q('#results button.result')?.textContent.replace(/\s+/g,' ').trim().slice(0,40);
  if(q('#results button.result')){ click(q('#results button.result')); await wait(3000); }
  R.article = q('.hero h2')?.textContent;
  R.blocks = all('.sections .section h3').map(h=>h.textContent.trim().split('\n')[0]).slice(0,12);
  R.figures = all('.detail svg').length;
  R.copyright = !!q('.copyright');

  // radial
  click(q('#btn-radial'));
  for(let i=0;i<60;i++){if(q('.rad-node'))break;await wait(400);}
  await wait(1500);
  R.radialNodes = all('.rad-node').length;
  R.radialStat = q('.rad-stat')?.textContent;
  click(q('#btn-radial-close')); await wait(300);

  // travel
  click(q('#btn-travel'));
  for(let i=0;i<40;i++){if(q('#travel-countries option'))break;await wait(300);}
  R.countries = all('#travel-countries option').length;
  q('#travel-country').value='Sri Lanka'; q('#travel-days').value='11';
  q('#travel-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.trow'))break;await wait(300);}
  R.travelRows = all('.trow').length;
  R.nipahBadge = [...all('.trow')].find(t=>/Nipah/.test(t.textContent))?.querySelector('.trow-ev')?.textContent;

  // differential
  click(q('#btn-dx'));
  for(let i=0;i<40;i++){if(q('#dx-syndrome option'))break;await wait(300);}
  q('#dx-syndrome').value='encephalitis'; q('#dx-country').value='Sri Lanka';
  q('#dx-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.dx-out .trow'))break;await wait(300);}
  R.dxRows = all('.dx-out .trow').length;
  R.dxHasJE = all('.dx-out .trow-name').some(n=>/Japanese encephalitis/.test(n.textContent));

  // pathogen index
  click(q('#btn-pathogens'));
  for(let i=0;i<40;i++){if(q('.pix-q'))break;await wait(300);}
  R.pathogenCount = q('.pix-count')?.textContent;

  console.log(JSON.stringify(R,null,1));
  console.log('\nERRORS:', errors.length?errors.slice(0,6):'none');
  window.close(); process.exit(errors.length?1:0);
})();
