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
      const ce=w.console.error;w.console.error=(...a)=>{errors.push('console.error: '+a.join(' '));ce(...a);};
    }});
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}
  q('#btn-dx').dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<40;i++){if(q('#dx-syndrome option'))break;await wait(300);}
  const out={};
  for (const [country,days] of [['Sri Lanka',''],['Sri Lanka','9'],['India','']]) {
    q('#dx-syndrome').value='encephalitis';
    q('#dx-country').value=country; q('#dx-days').value=days;
    q('#dx-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
    for(let i=0;i<40;i++){if(q('.dx-out .trow'))break;await wait(300);}
    await wait(500);
    const rows=all('.dx-out .trow').map(t=>({
      name:t.querySelector('.trow-name')?.textContent,
      scope:t.querySelector('.trow-scope')?.textContent}));
    out[`${country}${days?' day '+days:''}`]={
      rendered:rows.length,
      apiSaid:(await (await window.fetch(`${BASE}/api/differential?syndrome=encephalitis&country=${encodeURIComponent(country)}${days?'&days='+days:''}`)).json()).counts.total,
      JEpresent:rows.some(r=>/Japanese encephalitis/i.test(r.name||'')),
      names:rows.map(r=>r.name)};
  }
  console.log(JSON.stringify(out,null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
