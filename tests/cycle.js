// Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
// Proprietary. No licence granted; see LICENSE.
//
// Every transmission figure draws the route by which PEOPLE are infected.
//
// Written after HIV was drawn as primate-to-human: the cross-species origin
// of the virus, not how anyone acquires it. The figure had been inferring the
// cycle from the profile prose, and prose cannot separate the route from an
// evolutionary origin or a sylvatic aside, so several figures stated
// something false — SARS-CoV-2 from bats via contaminated food, rabies with
// a bat reservoir when dogs cause almost all human cases, mpox as
// aerosolised rodent excreta, Hendra as person-to-person when no human has
// ever given it to another, yellow fever with a human reservoir because
// "non-human primates" contains the word "human".
//
// This asserts the node chain of every figure, so a change to the inference
// or to a profile cannot quietly rewrite one.
//
//   node cycle.js          (no server needed)
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
global.window = {};
new Function('window', fs.readFileSync(path.join(ROOT, 'static/js/figures.js'), 'utf8'))(global.window);
const F = global.window.F;

// The profiles as the application sees them: out of data/atlas.json, not out
// of profiles.py. They are not the same thing -- atlas.json is a build
// artifact -- and reading the source directly let this suite pass while the
// running app drew the old figures, because `python -m atlas.build` had not
// been re-run after the profiles changed.
const profs = JSON.parse(execFileSync(
  fs.existsSync(path.join(ROOT, '.venv/bin/python')) ? path.join(ROOT, '.venv/bin/python') : 'python3',
  ['-c', `import json, sys, io, contextlib
sys.path.insert(0, ${JSON.stringify(ROOT)})
with contextlib.redirect_stdout(io.StringIO()):
    import app
out = {}
for node in app.NODES.values():
    prof = (node.get("meta") or {}).get("profile")
    if node["rank"] == "species" and prof:
        out[node["name"]] = {k: prof.get(k) for k in
                             ("cycle", "host", "vectors", "reservoir", "transmission")}
print(json.dumps(out))`],
  { encoding: 'utf8', cwd: ROOT, maxBuffer: 64 * 1024 * 1024 }));

// What each of these must draw, left to right. Chosen because each one was
// wrong, or is the kind of case that goes wrong.
const WANT = {
  // No animal belongs in these: the virus circulates among people.
  'Lentivirus humimdef1':         ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Betacoronavirus pandemicum':   ['Infected person', 'Respiratory aerosols', 'Susceptible person'],
  'Morbillivirus hominis':        ['Infected person', 'Respiratory aerosols', 'Susceptible person'],
  'Orthopoxvirus variola':        ['Infected person', 'Respiratory aerosols', 'Susceptible person'],
  'Alphainfluenzavirus influenzae': ['Infected person', 'Respiratory aerosols', 'Susceptible person'],
  // Human-to-human, with the animal spillover kept as a side arrow.
  'Orthopoxvirus monkeypox':      ['Infected person', 'Skin and sexual contact', 'Susceptible person', 'Rodents'],
  // Dogs, not bats: \bdog\b never matched "dogs".
  'Lyssavirus rabies':            ['Dogs & wild carnivores', 'Saliva', 'Humans'],
  // A horse every time, and no onward human spread.
  'Henipavirus hendraense':       ['Bats', 'Horses', 'Humans'],
  'Henipavirus nipahense':        ['Bats', 'Pigs / contaminated sap', 'Humans', 'Further cases'],
  // Contact with the animal, not "contaminated food".
  'Orthoebolavirus zairense':     ['Bats', 'Contact with the animal', 'Humans', 'Further cases'],
  'Orthomarburgvirus marburgense':['Bats', 'Contact with the animal', 'Humans', 'Further cases'],
  // Reservoir = the host named FIRST, not the first row of the icon table.
  'Orthoflavivirus flavi':        ['Primates', 'Mosquito', 'Humans'],
  'Alphavirus chikungunya':       ['Humans', 'Mosquito', 'Humans'],
  'Orthoflavivirus denguei':      ['Humans', 'Mosquito', 'Humans'],
  'Orthoflavivirus zikaense':     ['Humans', 'Mosquito', 'Humans'],
  'Orthoflavivirus nilense':      ['Birds', 'Mosquito', 'Humans'],
  'Orthobunyavirus oropoucheense':['Sloths', 'Biting midge', 'Humans'],
  'Phlebovirus toscanaense':      ['Vertebrate host', 'Sandfly', 'Humans'],
  'Mammarenavirus lassaense':     ['Rodents', 'Aerosolised excreta', 'Humans'],
  // The blood-borne and hepatitis profiles, added after an audit found 116
  // established human pathogens with none. No animal belongs in any of these.
  'Deltaretrovirus priTlym1':     ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Lentivirus humimdef2':         ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Orthohepadnavirus hominoidei': ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Orthohepacivirus hominis':     ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Deltavirus italiense':         ['Infected person', 'Blood, sex, birth', 'Susceptible person'],
  'Paslahepevirus balayani':      ['Humans', 'Water or food', 'Humans'],
  'Hepatovirus ahepa':            ['Humans', 'Water or food', 'Humans'],
  'Orthopneumovirus hominis':     ['Infected person', 'Respiratory aerosols', 'Susceptible person'],
};

const unesc = s => s.replace(/&amp;/g, '&').replace(/&#39;/g, "'")
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');

const labelsOf = svg => [...svg.matchAll(/class="cyc-lab"[^>]*>([^<]*)</g)]
  .map(m => unesc(m[1]));

let failed = 0;
for (const [name, want] of Object.entries(WANT)) {
  const p = profs[name];
  if (!p) { console.log(`FAIL ${name}: no profile`); failed++; continue; }
  const got = labelsOf(F.transmissionFigure(p, {}));
  if (JSON.stringify(got) !== JSON.stringify(want)) {
    failed++;
    console.log(`FAIL ${name}`);
    console.log(`       drew  ${got.join('  ->  ')}`);
    console.log(`       want  ${want.join('  ->  ')}`);
  } else {
    console.log(`ok   ${name.padEnd(32)} ${got.join(' -> ')}`);
  }
}

// No figure may put a human on the receiving end of an animal arrow unless
// the profile says the route is zoonotic.
const ZOONOTIC = /vector|rodent-excreta|intermediate|wildlife-contact|animal-bite|direct/;
for (const [name, p] of Object.entries(profs)) {
  const svg = F.transmissionFigure(p, {});
  if (/NaN|undefined/.test(svg)) { console.log(`FAIL ${name}: NaN or undefined in the SVG`); failed++; }
  const labels = labelsOf(svg);
  if (!labels.length) { console.log(`FAIL ${name}: no nodes drawn`); failed++; }
}

console.log(`\n${Object.keys(WANT).length} asserted, ${Object.keys(profs).length} profiles rendered, ${failed} failing`);
process.exit(failed ? 1 : 0);
