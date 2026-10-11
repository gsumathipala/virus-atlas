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
      const ce=w.console.error;w.console.error=(...a)=>{errors.push('console.error: '+a.join(' '));ce(...a);};
    }});
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}
  const R={};
  // mpox has three builds
  q('#q').value='monkeypox virus';
  q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500);
  q('#results button.result').dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<60;i++){if(q('.genomic:not([hidden])'))break;await wait(500);}
  R.species=q('.hero h2')?.textContent;
  R.genomicShown=!!q('.genomic:not([hidden])');
  R.builds=all('.gb').map(b=>b.querySelector('a')?.textContent);
  R.meta=all('.gb-meta').map(m=>m.textContent.replace(/\s+/g,' ').trim());
  R.links=all('.gb a[href]').map(a=>a.getAttribute('href'));
  // a species with no build must show nothing rather than an empty box
  q('#q').value='Orthobunyavirus catqueense';
  q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500);
  q('#results button.result').dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  await wait(3000);
  R.oyaGenomicHidden=!q('.genomic:not([hidden])');
  console.log(JSON.stringify(R,null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
