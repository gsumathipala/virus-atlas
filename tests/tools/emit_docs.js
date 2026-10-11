// Render real app SVG into files for the repository's docs.
// These are the app's own vector output, captured from a live page in jsdom —
// not browser screenshots, which this environment cannot take.
const { JSDOM } = require('jsdom');
const fs = require('fs'), path = require('path');
const BASE = 'http://127.0.0.1:5057';
const OUT = path.join(__dirname, 'docsvg');

function matrixFrom(str) {
  let m = [1,0,0,1,0,0];
  const mul=(x,y)=>[x[0]*y[0]+x[2]*y[1],x[1]*y[0]+x[3]*y[1],x[0]*y[2]+x[2]*y[3],
                    x[1]*y[2]+x[3]*y[3],x[0]*y[4]+x[2]*y[5]+x[4],x[1]*y[4]+x[3]*y[5]+x[5]];
  for (const op of String(str||'').matchAll(/(\w+)\s*\(([^)]*)\)/g)) {
    const n=op[2].split(/[\s,]+/).filter(Boolean).map(Number);
    if(op[1]==='translate') m=mul(m,[1,0,0,1,n[0]||0,n[1]||0]);
    else if(op[1]==='rotate'){const r=(n[0]||0)*Math.PI/180;
      m=mul(m,[Math.cos(r),Math.sin(r),-Math.sin(r),Math.cos(r),0,0]);}
    else if(op[1]==='scale') m=mul(m,[n[0]??1,0,0,n[1]??n[0]??1,0,0]);
  }
  return {a:m[0],b:m[1],c:m[2],d:m[3],e:m[4],f:m[5]};
}
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const html=await (await fetch(BASE+'/')).text();
  const dom=new JSDOM(html,{url:BASE+'/',runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,
    beforeParse(w){w.fetch=(...a)=>fetch(...a);w.Element.prototype.scrollIntoView=function(){};
      w.SVGElement.prototype.getScreenCTM=()=>({a:1,b:0,c:0,d:1,e:0,f:0,inverse(){return this;},multiply(){return this;}});
      w.SVGElement.prototype.createSVGPoint=()=>({x:0,y:0,matrixTransform(){return{x:0,y:0};}});
      Object.defineProperty(w.SVGElement.prototype,'transform',{configurable:true,
        get(){const s=this;return{baseVal:{numberOfItems:1,
          consolidate(){return{matrix:matrixFrom(s.getAttribute('transform'))};}}};}});
    }});
  const {window}=dom,doc=window.document,q=s=>doc.querySelector(s),all=s=>[...doc.querySelectorAll(s)];
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const click=e=>e.dispatchEvent(new window.MouseEvent('click',{bubbles:true}));
  for(let i=0;i<60;i++){if(q('.hero h2'))break;await wait(500);}

  const save=(name,svg,w=900,h=620)=>{
    const c=svg.cloneNode(true);
    c.setAttribute('xmlns','http://www.w3.org/2000/svg');
    c.setAttribute('width',w); c.setAttribute('height',h);
    fs.writeFileSync(path.join(OUT,name+'.svg'),c.outerHTML);
    console.log('  wrote',name);
  };

  // Figures from the Oya virus page — the virus that started the project.
  q('#q').value='Oya virus'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1600); click(q('#results button.result')); await wait(3000);
  const figs=all('.detail svg');
  console.log('oya page SVG count:', figs.length);
  figs.forEach((f,i)=>{ if(i<6) save(`oya-fig${i}`, f, 760, 520); });

  // Radial tree, split mode at the top of the taxonomy.
  click(q('#btn-radial'));
  for(let i=0;i<50;i++){if(q('.rad-node'))break;await wait(400);}
  await wait(2500);
  const crumb=all('.rad-crumbs button')[0];
  if(crumb){click(crumb); await wait(3500);}
  if(q('.rad-svg')) save('radial-split', q('.rad-svg'), 1000, 1000);

  // Radial tree rooted on Orthobunyavirus.
  const ob=all('.rad-crumbs button').find(b=>/Orthobunyavirus/.test(b.textContent));
  q('#btn-radial-close') && click(q('#btn-radial-close'));
  await wait(400);
  q('#q').value='Oya virus'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1500); click(q('#results button.result')); await wait(2500);
  click(q('#btn-radial'));
  for(let i=0;i<50;i++){if(q('.rad-node'))break;await wait(400);}
  await wait(3000);
  if(q('.rad-svg')) save('radial-orthobunyavirus', q('.rad-svg'), 1000, 1000);

  // World map from a species with a wide range.
  q('#btn-radial-close') && click(q('#btn-radial-close')); await wait(300);
  q('#q').value='dengue'; q('#q').dispatchEvent(new window.Event('input',{bubbles:true}));
  await wait(1600); click(q('#results button.result')); await wait(3500);
  const map=all('.detail svg').find(s=>s.querySelector('.geo-country, path[class*="geo"]'));
  if(map) save('map-dengue', map, 900, 480);
  else console.log('  (no map svg found)');

  window.close();
})();
