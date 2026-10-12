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
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}
  const R={};
  // species blocks on a rich virus
  q('#q').value='Nipah'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500); click(q('#results button.result')); await wait(2600);
  R.blocks=all('.sections .section h3').map(h=>h.textContent.trim());
  R.baltimore=q('.balt-roman')?.textContent;
  R.receptors=all('.rc-row .pill').map(p=>p.textContent).slice(0,3);
  R.bsl=q('.bsl-badge')?.textContent;
  R.selectAgent=q('.bsl-sa')?.textContent;
  R.cmNone=q('.cm-none')?.textContent;
  R.syndromeChips=all('[data-syndrome]').map(c=>c.textContent.trim());
  // a cross-reacting virus
  q('#q').value='Oya virus'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500); click(q('#results button.result')); await wait(2600);
  R.oyaXR=all('.xr h4').map(h=>h.textContent.replace(/\s+/g,' ').trim());
  // differential panel
  click(q('#btn-dx'));
  for(let i=0;i<40;i++){if(q('#dx-syndrome option'))break;await wait(300);}
  R.dxView=q('.layout').dataset.view;
  R.syndromeOptions=all('#dx-syndrome option').length;
  R.routeOptions=all('#dx-route option').length;
  q('#dx-syndrome').value='haemorrhagic';
  q('#dx-country').value='Uganda';
  q('#dx-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.dx-out .trow'))break;await wait(300);}
  await wait(400);
  R.dxHeading=q('.dx-out .travel-summary h3')?.textContent;
  R.dxCount=q('.dx-out .travel-counts')?.textContent.replace(/\s+/g,' ').trim().slice(0,110);
  R.dxRows=all('.dx-out .trow').map(t=>({
    name:t.querySelector('.trow-name')?.textContent,
    score:t.querySelector('.trow-score')?.textContent})).slice(0,5);
  R.dxCaveatMentionsMalaria=/malaria/i.test(q('.travel-caveat')?.textContent||'');
  // click through to a virus
  click(q('.dx-out .trow')); await wait(2400);
  R.afterClick={view:q('.layout').dataset.view, article:q('.hero h2')?.textContent};
  // syndrome chip loop
  const chip=all('[data-syndrome]')[0];
  if(chip){ click(chip); for(let i=0;i<40;i++){if(q('.dx-out .trow'))break;await wait(300);} await wait(300);
    R.chipLoop={view:q('.layout').dataset.view, heading:q('.dx-out .travel-summary h3')?.textContent}; }
  console.log(JSON.stringify(R,null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
