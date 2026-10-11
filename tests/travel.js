// Travel panel, signals modal and pathogen index filter, driven through the DOM.
const { JSDOM } = require('jsdom');
const BASE='http://127.0.0.1:5057'; const errors=[];
(async()=>{
  const html=await (await fetch(BASE+'/')).text();
  const dom=new JSDOM(html,{url:BASE+'/',runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,
    beforeParse(w){w.fetch=(...a)=>fetch(...a);w.Element.prototype.scrollIntoView=function(){};
      w.SVGElement.prototype.getScreenCTM=()=>({a:1,b:0,c:0,d:1,e:0,f:0,inverse(){return this;},multiply(){return this;}});
      w.SVGElement.prototype.createSVGPoint=()=>({x:0,y:0,matrixTransform(){return{x:0,y:0};}});
      Object.defineProperty(w.SVGElement.prototype,'transform',{configurable:true,get(){return{baseVal:{numberOfItems:0,consolidate:()=>null}};}});
      w.addEventListener('error',e=>errors.push('error: '+e.message));
      w.onunhandledrejection=e=>errors.push('rejection: '+(e.reason?.message||e.reason));
      const ce=w.console.error; w.console.error=(...a)=>{errors.push('console.error: '+a.join(' '));ce(...a);};
    }});
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}
  const R={};

  // --- travel panel ---
  click(q('#btn-travel'));
  for(let i=0;i<30;i++){if(q('#travel-countries option'))break;await wait(300);}
  R.panelOpen=!q('#travel-panel').hidden;
  R.layoutClass=q('.layout').className;
  R.countryOptions=all('#travel-countries option').length;
  q('#travel-country').value='Uganda'; q('#travel-days').value='11';
  q('#travel-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.travel-summary'))break;await wait(300);}
  await wait(400);
  R.heading=q('.travel-summary h3')?.textContent;
  R.counts=q('.travel-counts')?.textContent.replace(/\s+/g,' ').trim().slice(0,150);
  R.groups=all('.travel-block h4').map(h=>h.textContent.replace(/\s+/g,' ').trim());
  R.rows=all('.trow').length;
  R.windows=[...new Set(all('.trow').map(t=>t.dataset.window))];
  R.hasLinks=all('.trow[data-goto]').length;
  R.liveBlock=!!q('.travel-live');
  R.caveat=!!q('.travel-caveat');

  // clicking a listed virus must open it in the article panel
  const row=all('.trow[data-goto]')[0];
  R.clicked=row.querySelector('.trow-sp')?.textContent;
  click(row); await wait(2200);
  R.openedArticle=q('.hero h2')?.textContent;

  // --- signals modal ---
  click(q('#btn-signals'));
  for(let i=0;i<40;i++){if(q('.sig-full li'))break;await wait(300);}
  R.signalRows=all('.sig-full li').length;
  R.signalKinds=[...new Set(all('.sig-full li').map(l=>l.dataset.kind))];
  R.signalSrc=q('.sig-src')?.textContent.replace(/\s+/g,' ').trim();
  R.modalTitle=q('#modal-title')?.textContent;

  // --- pathogen index, now including herpesviruses ---
  q('[data-close]') && click(q('[data-close]'));
  await wait(200);
  click(q('#btn-pathogens'));
  for(let i=0;i<40;i++){if(q('.pix-q'))break;await wait(300);}
  await wait(300);
  R.pixTitle=q('#modal-title')?.textContent;
  R.pixTotal=q('.pix-count')?.textContent;
  q('.pix-q').value='herpes';
  q('.pix-q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(300);
  R.herpesFiltered=q('.pix-count')?.textContent;
  R.herpesNames=all('.pix-results .row-btn, .pix-results button').slice(0,6)
    .map(b=>b.textContent.replace(/\s+/g,' ').trim().slice(0,46));

  console.log(JSON.stringify(R,null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
