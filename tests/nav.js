// Selecting a virus from ANY source must move the tree to it.
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
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}
  const R={};

  // Is the selected node present AND marked selected in the tree?
  const treeState=()=>{
    const sel=q('.tree-node.selected, .tree-row.selected, [aria-selected="true"]');
    const id=sel?.closest('.tree-node')?.dataset.id || sel?.dataset.id || null;
    return {view:q('.layout').dataset.view,
            treeShown:window.getComputedStyle(q('#tree-panel')).display!=='none',
            selectedInTree:id, article:q('.hero h2')?.textContent};
  };

  // 1. from search
  q('#q').value='Nipah'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500); click(q('#results button.result')); await wait(2300);
  R.fromSearch=treeState();

  // 2. from travel (overlay must step aside and tree must move)
  click(q('#btn-travel')); await wait(1300);
  q('#travel-country').value='Sri Lanka';
  q('#travel-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  for(let i=0;i<40;i++){if(q('.trow'))break;await wait(300);}
  R.sriLankaRows=all('.trow').map(t=>({
    name:t.querySelector('.trow-name')?.textContent,
    ev:t.querySelector('.trow-ev')?.textContent||'human cases'}));
  const nipah=all('.trow').find(t=>/Nipah/.test(t.textContent));
  R.nipahBadge=nipah?.querySelector('.trow-ev')?.textContent;
  const dengueRow=all('.trow').find(t=>/dengue/i.test(t.textContent));
  click(dengueRow); await wait(2400);
  R.fromTravel=treeState();

  // 3. from the pathogen index
  click(q('#btn-pathogens'));
  for(let i=0;i<40;i++){if(q('.pix-q'))break;await wait(300);}
  q('.pix-q').value='hepatitis E';
  q('.pix-q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(400);
  const hev=q('.pix-results button');
  R.hevInIndex=hev?.textContent.replace(/\s+/g,' ').trim().slice(0,50);
  click(hev); await wait(2400);
  R.fromIndex={...treeState(), modalClosed:q('#modal').hidden};

  // 4. from signals
  click(q('#btn-signals'));
  for(let i=0;i<40;i++){if(q('.sig-full li'))break;await wait(300);}
  const sig=all('.sig-full [data-goto]')[0];
  R.signalLabel=sig?.textContent;
  click(sig); await wait(2400);
  R.fromSignals={...treeState(), modalClosed:q('#modal').hidden};

  R.allMovedTree=[R.fromSearch,R.fromTravel,R.fromIndex,R.fromSignals]
    .every(s=>s.treeShown && s.view==='tree' && s.selectedInTree);
  console.log(JSON.stringify(R,null,1));
  console.log('\nERRORS:',errors.length?errors:'none');
  window.close(); process.exit(errors.length?1:0);
})();
