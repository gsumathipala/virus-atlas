// Emit raw figure SVGs to disk for visual QA.
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');
const BASE = 'http://127.0.0.1:5057';
const OUT = path.join(__dirname, 'svg');

const SPECS = {
  peribunya: { family: 'Peribunyaviridae', genome: 'ssRNA(-)' },
  corona:    { family: 'Coronaviridae', genome: 'ssRNA(+)' },
  rhabdo:    { family: 'Rhabdoviridae', genome: 'ssRNA(-)' },
  filo:      { family: 'Filoviridae', genome: 'ssRNA(-)' },
  picorna:   { family: 'Picornaviridae', genome: 'ssRNA(+)' },
  adeno:     { family: 'Adenoviridae', genome: 'dsDNA' },
  pox:       { family: 'Poxviridae', genome: 'dsDNA' },
  phage:     { family: 'Straboviridae', genome: 'dsDNA' },
  orthomyxo: { family: 'Orthomyxoviridae', genome: 'ssRNA(-)' },
  flavi:     { family: 'Flaviviridae', genome: 'ssRNA(+)' },
  virga:     { family: 'Virgaviridae', genome: 'ssRNA(+)' },
  fusello:   { family: 'Fuselloviridae', genome: 'dsDNA' },
  mimi:      { family: 'Mimiviridae', genome: 'dsDNA' },
  paramyxo:  { family: 'Paramyxoviridae', genome: 'ssRNA(-)' },
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const html = await (await fetch(BASE + '/')).text();
  const dom = new JSDOM(html, {
    url: BASE + '/', runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (...a) => fetch(...a);
      w.Element.prototype.scrollIntoView = function () {};
    },
  });
  const { window } = dom;
  for (let i = 0; i < 60; i++) {
    if (window.F) break;
    await new Promise(r => setTimeout(r, 400));
  }

  // Morphology specs come from the server so the drawings match the real app.
  for (const [name, q] of Object.entries(SPECS)) {
    const r = await fetch(`${BASE}/api/search?q=${encodeURIComponent(q.family)}`);
    const res = (await r.json()).results.find(x => x.rank === 'family')
             || (await (await fetch(`${BASE}/api/search?q=${encodeURIComponent(q.family)}`)).json()).results[0];
    if (!res) { console.log('no node for', q.family); continue; }
    const node = await (await fetch(`${BASE}/api/node?id=${encodeURIComponent(res.id)}`)).json();
    const spec = node.morphology;
    if (!spec) { console.log('no spec for', q.family); continue; }
    fs.writeFileSync(path.join(OUT, `virion-${name}.svg`), window.F.virionFigure(spec));
    fs.writeFileSync(path.join(OUT, `genome-${name}.svg`), window.F.genomeFigure(spec));
  }

  // Transmission cycles, from the real profiles.
  const cycles = {
    oya: 'Orthobunyavirus catqueense',
    lassa: 'Mammarenavirus lassaense',
    nipah: 'Henipavirus nipahense',
    measles: 'Morbillivirus hominis',
    tbe: 'Orthoflavivirus neudoerflense',
    dengue: 'Orthoflavivirus denguei',
  };
  for (const [name, species] of Object.entries(cycles)) {
    const s = await (await fetch(`${BASE}/api/search?q=${encodeURIComponent(species)}`)).json();
    const hit = s.results.find(x => x.rank === 'species');
    const node = await (await fetch(`${BASE}/api/node?id=${encodeURIComponent(hit.id)}`)).json();
    const p = node.meta.profile;
    fs.writeFileSync(path.join(OUT, `cycle-${name}.svg`),
      window.F.transmissionFigure(p, node.meta));
    if (node.geo && node.geo.countries.length) {
      const w = await (await fetch(`${BASE}/static/data/world.json`)).json();
      fs.writeFileSync(path.join(OUT, `map-${name}.svg`),
        window.F.mapFigure(w, node.geo.countries, { worldwide: node.geo.worldwide }));
    }
  }

  // The organism cartoons, all together.
  const names = Object.keys(window.F.ICON);
  const cols = 6, cell = 90;
  const rows = Math.ceil(names.length / cols);
  let g = '';
  names.forEach((n, i) => {
    const x = (i % cols) * cell + cell / 2;
    const y = Math.floor(i / cols) * cell + cell / 2 - 8;
    g += `<circle class="cyc-disc" cx="${x}" cy="${y}" r="32"/>`;
    g += window.F.icon(n, x, y, 44);
    g += `<text class="cyc-lab" x="${x}" y="${y + 46}" text-anchor="middle">${n}</text>`;
  });
  fs.writeFileSync(path.join(OUT, 'icons-all.svg'),
    `<svg class="fig fig-cycle" viewBox="0 0 ${cols * cell} ${rows * cell}">${g}</svg>`);

  console.log('wrote', fs.readdirSync(OUT).length, 'svg files');
  window.close();
})();
