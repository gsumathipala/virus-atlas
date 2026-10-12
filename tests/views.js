// Only one left-column panel may ever be visible, and every route back works.
const { JSDOM } = require('jsdom');
const BASE = process.env.BASE || 'http://127.0.0.1:5057'; const errors=[];
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
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s);
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  const vis=s=>{const e=q(s);return e && !e.hidden && window.getComputedStyle(e).display!=='none';};
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}

  const state=label=>({
    step:label,
    view:q('.layout').dataset.view,
    treeVisible:vis('#tree-panel'),
    radialVisible:vis('#radial-panel'),
    travelVisible:vis('#travel-panel'),
    sideVisible:vis('#side'),
    pressed:{radial:q('#btn-radial').getAttribute('aria-pressed'),
             travel:q('#btn-travel').getAttribute('aria-pressed')},
  });
  const log=[state('initial')];
  const only=s=>[s.treeVisible,s.radialVisible,s.travelVisible].filter(Boolean).length===1;

  click(q('#btn-travel')); await wait(1500); log.push(state('travel open'));
  click(q('#btn-radial')); await wait(2500); log.push(state('radial from travel'));
  click(q('#btn-travel')); await wait(1200); log.push(state('travel from radial'));
  click(q('#btn-tree'));   await wait(500);  log.push(state('tree button returns'));
  click(q('#btn-radial')); await wait(2500); log.push(state('radial again'));
  doc.dispatchEvent(new window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  await wait(500); log.push(state('escape returns'));

  // Travel -> pick a virus -> must land back in tree view with the article
  click(q('#btn-travel')); await wait(1200);
  q('#travel-country').value='Sri Lanka';
  q('#travel-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.trow'))break;await wait(300);}
  const row=q('.trow[data-goto]');
  const picked=row?.querySelector('.trow-sp')?.textContent;
  click(row); await wait(2300);
  log.push(state('after picking a virus'));

  console.log(JSON.stringify({
    picked,
    exactlyOnePanelAtEveryStep: log.every(only),
    pressedAlwaysMatches: log.every(s =>
      (s.pressed.radial==='true')===(s.view==='radial') &&
      (s.pressed.travel==='true')===(s.view==='travel')),
    articleAfterPick: q('.hero h2')?.textContent,
    steps: log,
  },null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
