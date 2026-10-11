// Verify the figure engine renders real geometry for every shape, and that the
// plates appear in the sidebar.
const { JSDOM } = require('jsdom');
const BASE = 'http://127.0.0.1:5057';
const errors = [];

(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/', runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
      w.addEventListener('error', e => errors.push('error: ' + e.message));
      w.onunhandledrejection = e => errors.push('rejection: ' + (e.reason?.message || e.reason));
      const ce = w.console.error;
      w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); ce(...a); };
    },
  });
  const { window } = dom, doc = window.document, q = s => doc.querySelector(s);
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60; i++) { if (q('.hero h2')) break; await wait(500); }

  const report = {};

  // --- every morphology shape must produce drawable geometry
  const shapes = ['spherical', 'pleomorphic', 'icosahedral', 'bullet', 'filament',
                  'rod', 'brick', 'phage', 'lemon', 'bottle', 'capsidless'];
  report.shapeGeometry = {};
  for (const shape of shapes) {
    const spec = {
      shape, envelope: shape !== 'icosahedral' && shape !== 'rod' && shape !== 'phage',
      spikes: shape === 'icosahedral' ? 'fibre' : 'spike',
      capsid: shape === 'capsidless' ? 'none' : (shape === 'icosahedral' ? 'icosahedral' : 'helical'),
      nm: shape === 'capsidless' ? [0, 0] : [80, 120],
      segments: 3, kb: 12, genes: ['L', 'M', 'S'],
      genome: 'ssRNA(-)', shape_label: shape, confident: true,
    };
    const svg = window.F.virionFigure(spec);
    const frag = JSDOM.fragment(`<div>${svg}</div>`);
    const el = frag.firstChild;
    const paths = [...el.querySelectorAll('path')].map(p => p.getAttribute('d') || '');
    report.shapeGeometry[shape] = {
      bytes: svg.length,
      nodes: el.querySelectorAll('*').length,
      labels: el.querySelectorAll('.fig-lab, .fig-in').length,
      badNumbers: /NaN|undefined|Infinity/.test(svg),
      emptyPaths: paths.filter(d => !d.trim()).length,
      hasScaleBar: /class="scale"/.test(svg),
    };
  }

  // --- genome figure for a segmented and an unsegmented genome
  const g3 = window.F.genomeFigure({ segments: 3, genes: ['L — pol', 'M — Gn/Gc', 'S — N'], genome: 'ssRNA(-)', kb: 12 });
  const g1 = window.F.genomeFigure({ segments: 1, genes: ['gag', 'pol', 'env'], genome: 'ssRNA-RT', kb: 9.7 });
  report.genome = {
    segmentedRows: (g3.match(/gen-seg/g) || []).length,
    segmentedBlocks: (g3.match(/gen-block/g) || []).length,
    monoBlocks: (g1.match(/gen-block/g) || []).length,
    bad: /NaN|undefined/.test(g3 + g1),
  };

  // --- transmission cycle picks the right cartoons
  const cases = {
    midgeVector: { vectors: ['Culicoides spp. (biting midges)'], reservoir: 'Domestic pigs', transmission: 'Arboviral — bite of midges.' },
    rodentBorne: { vectors: ['None (rodent-borne)'], reservoir: 'Mastomys natalensis rodents', transmission: 'Inhalation of aerosolised rodent excreta.' },
    batBorne: { vectors: ['None (bat reservoir, with intermediate hosts)'], reservoir: 'Pteropus fruit bats', transmission: 'Consumption of date palm sap; person-to-person including nosocomial spread.' },
    respiratory: { vectors: ['None (respiratory)'], reservoir: 'Humans', transmission: 'Respiratory aerosols and droplets.' },
    tickBorne: { vectors: ['Ixodes ricinus'], reservoir: 'Small rodents', transmission: 'Tick bite.' },
  };
  report.cycles = {};
  for (const [k, p] of Object.entries(cases)) {
    const svg = window.F.transmissionFigure(p, {});
    report.cycles[k] = {
      icons: [...JSDOM.fragment(`<div>${svg}</div>`).firstChild.querySelectorAll('.icon')]
        .map(g => (g.getAttribute('class') || '').trim()).length,
      nodes: (svg.match(/cyc-node/g) || []).length,
      arrows: (svg.match(/class="flow"/g) || []).length,
      labels: [...svg.matchAll(/class="cyc-lab"[^>]*>([^<]*)</g)].map(m => m[1]),
      bad: /NaN|undefined/.test(svg),
    };
  }

  // --- the seed species page: plates present and captioned
  await wait(1500);
  report.seedPage = {
    title: q('.hero h2')?.textContent,
    heroVirion: !!q('.hero-art .fig-virion'),
    hostChips: [...doc.querySelectorAll('.host-chip')].map(c => c.textContent.trim()),
    plates: [...doc.querySelectorAll('.plate figcaption strong')].map(s => s.textContent),
    figNumbers: [...doc.querySelectorAll('.plate figcaption b')].map(s => s.textContent),
    virionLabels: [...doc.querySelectorAll('.hero-art .fig-lab')].map(t => t.textContent),
    genomeSegments: [...doc.querySelectorAll('.fig-genome .gen-seg')].map(t => t.textContent),
    cycleNodes: [...doc.querySelectorAll('.fig-cycle .cyc-lab')].map(t => t.textContent),
  };

  // --- the map loads and highlights the right countries
  for (let i = 0; i < 40; i++) { if (q('.fig-map')) break; await wait(500); }
  const on = [...doc.querySelectorAll('.fig-map .geo.on title')].map(t => t.textContent);
  report.map = {
    rendered: !!q('.fig-map'),
    totalCountries: doc.querySelectorAll('.fig-map .geo').length,
    highlighted: on.sort(),
    dots: doc.querySelectorAll('.fig-map .geo-dot').length,
  };

  // --- a family node gets its own particle + genome plate
  const input = q('#q');
  input.value = 'Filoviridae';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(1000);
  q('.result').click();
  await wait(1800);
  report.familyPage = {
    title: q('.hero h2')?.textContent,
    rank: q('.kicker')?.textContent,
    virion: !!q('.hero-art .fig-virion'),
    tierBarSegs: doc.querySelectorAll('.dist-bar span').length,
    plates: [...doc.querySelectorAll('.plate figcaption strong')].map(s => s.textContent),
  };

  // --- a phage, to exercise a very different shape end-to-end
  input.value = 'Straboviridae';
  input.dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(1000);
  q('.result').click();
  await wait(1800);
  report.phagePage = {
    title: q('.hero h2')?.textContent,
    hasTail: !!q('.fig-virion .tail'),
    hasFibres: doc.querySelectorAll('.fig-virion .fibre').length,
    labels: [...doc.querySelectorAll('.hero-art .fig-lab')].map(t => t.textContent),
  };

  console.log(JSON.stringify(report, null, 1));
  console.log('\nERRORS:', errors.length ? errors : 'none');
  window.close();
  process.exit(errors.length ? 1 : 0);
})();
