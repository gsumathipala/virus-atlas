/*! Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
 *  Proprietary. No licence granted; see LICENSE. */
/* Virus Atlas -- tree, search and the detail sidebar. */

const SEED = 'root/riboviria/orthornavirae/negarnaviricota/polyploviricotina/bunyaviricetes/elliovirales/peribunyaviridae/orthobunyavirus/simbu-serogroup/manzanilla-clade/orthobunyavirus-catqueense';

const el = {
  tree: document.getElementById('tree'),
  treeSub: document.getElementById('tree-sub'),
  side: document.getElementById('side'),
  legend: document.getElementById('legend'),
  q: document.getElementById('q'),
  results: document.getElementById('results'),
  modal: document.getElementById('modal'),
  radialPanel: document.getElementById('radial-panel'),
  radial: document.getElementById('radial'),
  modalBody: document.getElementById('modal-body'),
  travelPanel: document.getElementById('travel-panel'),
  dxPanel: document.getElementById('dx-panel'),
};

let TIERS = {};
let EPHEMERAL = false;   // set from /api/meta: host without persistent disk
let selected = null;
const nodeEls = new Map();   // node id -> .tree-node element

const api = (path, params) => {
  // Against the document base rather than the origin, so the app works
  // when served from a subpath. A leading slash would reset to the
  // root and undo that, so it is stripped.
  const url = new URL(String(path).replace(/^\//, ''), document.baseURI);
  Object.entries(params || {}).forEach(([k, v]) => v != null && url.searchParams.set(k, v));
  return fetch(url).then(r => {
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.json();
  });
};

const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const isBinomial = (name, rank) => rank === 'species' || rank === 'genus';

/* ----------------------------------------------------------------- tree */

function rowMarkup(n) {
  const leaf = n.n_children === 0;
  // Species and isolates carry their own tier; groups show the strongest beneath.
  const tier = (n.rank === 'species' || n.rank === 'isolate') ? n.tier : n.top_tier;
  const nameCls = isBinomial(n.name, n.rank) ? ' class="binomial"' : '';
  const count = n.rank === 'species'
    ? (n.n_isolates > 1 ? `${n.n_isolates} isolates` : '')
    : (n.n_species ? `${n.n_species.toLocaleString()} sp.` : '');

  return `
    <button class="tree-row" data-id="${esc(n.id)}" data-rank="${esc(n.rank)}"
            role="treeitem" aria-expanded="false">
      <span class="twist${leaf ? ' leaf' : ''}"><svg viewBox="0 0 10 10"><path d="M3 1l5 4-5 4z"/></svg></span>
      <span class="dot" data-tier="${esc(tier || 'no-evidence')}"></span>
      <span class="tree-label">
        <span class="tree-name"><span${nameCls}>${esc(n.name)}</span></span>
        ${n.common ? `<span class="tree-common">${esc(n.common)}</span>` : ''}
      </span>
      <span class="row-right">
        ${count ? `<span class="count">${esc(count)}</span>` : ''}
        <span class="rank-tag">${esc(n.rank)}</span>
      </span>
    </button>
    <div class="kids" role="group"></div>`;
}

function makeNode(n) {
  const node = document.createElement('div');
  node.className = 'tree-node';
  node.dataset.id = n.id;
  node.dataset.leaf = n.n_children === 0 ? '1' : '0';
  node.innerHTML = rowMarkup(n);
  nodeEls.set(n.id, node);
  return node;
}

async function expand(node) {
  const kids = node.querySelector(':scope > .kids');
  if (!kids.dataset.loaded) {
    kids.innerHTML = '<div class="loading-kid">loading…</div>';
    const data = await api('/api/children', { id: node.dataset.id });
    kids.innerHTML = '';
    data.children.forEach(c => kids.appendChild(makeNode(c)));
    kids.dataset.loaded = '1';
  }
  node.classList.add('open');
  node.querySelector(':scope > .tree-row').setAttribute('aria-expanded', 'true');
}

function collapse(node) {
  node.classList.remove('open');
  node.querySelector(':scope > .tree-row').setAttribute('aria-expanded', 'false');
}

async function toggle(node) {
  if (node.dataset.leaf === '1') return;
  node.classList.contains('open') ? collapse(node) : await expand(node);
}

function markSelected(id) {
  document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
  const node = nodeEls.get(id);
  if (node) node.querySelector(':scope > .tree-row').classList.add('selected');
  selected = id;
}

/** Expand every ancestor of `id`, then select and scroll it into view. */
async function reveal(id) {
  const parts = id.split('/');
  let acc = parts[0];
  for (let i = 1; i < parts.length; i++) {
    const node = nodeEls.get(acc);
    if (node) await expand(node);
    acc += '/' + parts[i];
  }
  const target = nodeEls.get(id);
  if (target) {
    target.querySelector(':scope > .tree-row')
      .scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
  markSelected(id);
}

async function select(id, { scroll = false } = {}) {
  markSelected(id);
  if (scroll) await reveal(id);
  await showDetail(id);
}

el.tree.addEventListener('click', async ev => {
  const row = ev.target.closest('.tree-row');
  if (!row) return;
  const node = row.parentElement;
  const id = row.dataset.id;
  // The twisty toggles; the label selects and, for internal nodes, also opens.
  if (ev.target.closest('.twist')) { await toggle(node); return; }
  await select(id);
  if (node.dataset.leaf !== '1' && !node.classList.contains('open')) await expand(node);
});

/* ------------------------------------------------------------- sidebar */

function tierBadge(tier) {
  if (!tier || !TIERS[tier]) return '';
  return `<span class="badge" data-tier="${esc(tier)}">
            <span class="dot" data-tier="${esc(tier)}"></span>${esc(TIERS[tier].label)}
          </span>`;
}

function crumbs(path) {
  return path.slice(1).map((p, i, arr) => {
    const last = i === arr.length - 1;
    const cls = isBinomial(p.name, p.rank) ? ' style="font-style:italic"' : '';
    return `<span class="crumb-rank">${esc(p.rank)}</span>` +
      (last
        ? `<span${cls}>${esc(p.name)}</span>`
        : `<button type="button" data-goto="${esc(p.id)}"${cls}>${esc(p.name)}</button><span class="sep">›</span>`);
  }).join(' ');
}

function distribution(tiers, total) {
  const order = Object.keys(TIERS);
  const present = order.filter(t => tiers[t]);
  if (!present.length || total === 0) return '';
  const bar = present.map(t =>
    `<span data-tier="${t}" style="width:${(tiers[t] / total * 100).toFixed(2)}%"></span>`).join('');
  const keys = present.map(t =>
    `<span class="dist-key"><span class="dot" data-tier="${t}"></span>
       <b>${tiers[t].toLocaleString()}</b> ${esc(TIERS[t].label.toLowerCase())}</span>`).join('');
  return `<div class="dist"><div class="dist-bar">${bar}</div><div class="dist-keys">${keys}</div></div>`;
}

const section = (title, body) => body
  ? `<section class="section"><h3>${esc(title)}</h3>${body}</section>` : '';

const para = text => text ? `<p>${esc(text)}</p>` : '';

function facts(pairs) {
  const items = pairs.filter(([, v]) => v && (!Array.isArray(v) || v.length))
    .map(([k, v]) => {
      const value = Array.isArray(v)
        ? `<div class="pills">${v.map(x => `<span class="pill">${esc(x)}</span>`).join('')}</div>`
        : esc(v);
      return `<div class="fact"><dt>${esc(k)}</dt><dd>${value}</dd></div>`;
    });
  return items.length ? `<dl class="facts">${items.join('')}</dl>` : '';
}

function refList(refs) {
  if (!refs || !refs.length) return '';
  const items = refs.map((r, i) => {
    const links = [];
    // DOIs contain slashes that must survive into the path, so no component encoding.
    if (r.doi) links.push(`<a href="https://doi.org/${esc(encodeURI(r.doi))}" target="_blank" rel="noopener">doi</a>`);
    if (r.pmid) links.push(`<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(r.pmid)}/" target="_blank" rel="noopener">PMID ${esc(r.pmid)}</a>`);
    if (r.url) links.push(`<a href="${esc(r.url)}" target="_blank" rel="noopener">link</a>`);
    return `<li class="ref"><span class="ref-n">${i + 1}</span>
      <span><span>${esc(r.label)}</span>
      ${links.length ? `<span class="ref-links">${links.join('')}</span>` : ''}</span></li>`;
  });
  return `<ul class="refs">${items.join('')}</ul>`;
}

function rowButton({ id, name, sub, meta, tier, italic }) {
  return `<button class="row-btn" type="button" data-goto="${esc(id)}">
      <span class="dot" data-tier="${esc(tier || 'no-evidence')}"></span>
      <span class="row-main">
        <span class="row-name">${italic ? `<span class="binomial">${esc(name)}</span>` : esc(name)}</span>
        ${sub ? `<span class="row-sub">${esc(sub)}</span>` : ''}
      </span>
      ${meta ? `<span class="row-meta">${esc(meta)}</span>` : ''}
    </button>`;
}

function isolateTable(isolates) {
  if (!isolates || !isolates.length) return '';
  const rows = isolates.map(iso => {
    const acc = iso.accession
      ? `<a href="https://www.ncbi.nlm.nih.gov/nuccore/${encodeURIComponent(iso.accession.split(/[;,\s]/)[0])}"
            target="_blank" rel="noopener">${esc(iso.accession)}</a>`
      : '—';
    return `<tr>
      <td><span class="iso-name">${esc((iso.names || []).join('; ') || '—')}</span>
          ${iso.exemplar ? ' <span class="tag-e">exemplar</span>' : ''}
          ${iso.abbrev?.length ? `<div class="iso-abbr">${esc(iso.abbrev.join('; '))}</div>` : ''}</td>
      <td>${esc(iso.designation || '—')}</td>
      <td>${acc}</td>
      <td>${esc(iso.host || '—')}</td>
    </tr>`;
  }).join('');
  return `<table class="iso-table">
      <thead><tr><th>Virus name</th><th>Isolate</th><th>GenBank</th><th>Host source</th></tr></thead>
      <tbody>${rows}</tbody></table>`;
}

/** Split "L: JX983194; M: JX983193; S: JX983192" into per-segment links. */
function accessionLinks(accession) {
  if (!accession) return '—';
  return accession.split(/\s*;\s*/).map(part => {
    const m = part.match(/^(?:([^:]+):\s*)?(\S+)$/);
    if (!m) return esc(part);
    const [, seg, acc] = m;
    const link = `<a href="https://www.ncbi.nlm.nih.gov/nuccore/${encodeURIComponent(acc)}"
        target="_blank" rel="noopener">${esc(acc)}</a>`;
    return seg ? `<span class="seg">${esc(seg)}</span> ${link}` : link;
  }).join('<br>');
}

function speciesDetail(d) {
  figN = 0;
  return speciesHead(d) + speciesPlates(d) + `<div class="sections">${speciesBody(d)}</div>`;
}

/** Numbered figure with a Nature-style caption. */
let figN = 0;
const figure = (svg, title, caption, cls = '') => {
  figN += 1;
  return `<figure class="plate ${cls}">
      <div class="plate-art">${svg}</div>
      <figcaption><b>Fig. ${figN}</b> <strong>${esc(title)}</strong> ${esc(caption)}</figcaption>
    </figure>`;
};

/* --------------------------------------------------------- tier provenance */

// Where a tier came from, in the reader's language. The point is that
// "unassessed" and "no human evidence" are different claims, and that a tier
// nobody checked should not look like a finding.
const BASIS = {
  profile: ['Curated profile', 'Assessed here against published evidence; see the citations below.'],
  reference: ['Reference list', 'Assigned from this project’s human-pathogen reference list.'],
  'vmr-name': ['Inferred from ICTV isolate names', 'The ICTV record names human-derived isolates, so human infection has been recorded. Disease causation has not been assessed.'],
  'host-range': ['Inferred from host range', 'ICTV records no vertebrate host, so human infection is not expected.'],
  none: ['Not assessed', 'Nobody has assessed this species here. That is not evidence against human infection.'],
  override: ['Corrected by you', 'This tier was set by hand and is stored locally.'],
};

function tierProvenance(d, m) {
  const basis = m.basis || 'none';
  const [label, why] = BASIS[basis] || BASIS.none;
  const ov = m.override;
  const note = ov?.note || m.tier_note || why;
  return `
    <div class="prov" data-basis="${esc(basis)}">
      <button class="prov-head" type="button" data-correct="${esc(d.id)}"
              aria-expanded="false" title="Correct this tier">
        <span class="prov-label">${esc(label)}</span>
        <span class="prov-why">${esc(note)}</span>
        <span class="prov-cta">Correct …</span>
      </button>
      ${ov ? `<p class="prov-was">was <b>${esc(TIERS[ov.was]?.label || ov.was || 'unknown')}</b>
               · changed ${esc((ov.at || '').replace('T', ' ').replace('Z', ' UTC'))}</p>` : ''}
    </div>`;
}

/** The inline tier editor, opened from the provenance line. */
function correctionForm(d, m) {
  const cur = m.tier;
  const opts = Object.entries(TIERS).map(([k, v]) =>
    `<option value="${esc(k)}"${k === cur ? ' selected' : ''}>${esc(v.label)}</option>`).join('');
  return `
    <form class="correct" data-species="${esc(d.name)}" data-id="${esc(d.id)}">
      <p class="correct-intro">
        Set the evidence tier for <i>${esc(d.name)}</i>. Corrections are keyed
        by species name and survive rebuilding the taxonomy from a new ICTV
        release.
      </p>
      ${EPHEMERAL ? `<p class="correct-warn">
        This instance has no persistent storage, so a correction lasts only
        until the server restarts or sleeps. Keep a note of anything you want
        to keep, or run the atlas locally, where it is written to
        <code>data/overrides.json</code>.
      </p>` : `<p class="correct-intro">Written to
        <code>data/overrides.json</code> on the server.</p>`}
      <label>Tier<select name="tier">${opts}</select></label>
      <label>Why <span class="opt">(optional, shown in place of the inferred note)</span>
        <input name="note" type="text" maxlength="400" autocomplete="off"
               value="${esc(m.override?.note || '')}"
               placeholder="e.g. Established cause of measles; vaccine-preventable">
      </label>
      <div class="correct-actions">
        <button class="btn btn-primary" type="submit">Save correction</button>
        ${m.basis === 'override'
          ? '<button class="btn" type="button" data-revert>Remove correction</button>' : ''}
        <button class="btn btn-quiet" type="button" data-cancel>Cancel</button>
      </div>
      <p class="correct-msg" role="status"></p>
    </form>`;
}

function speciesHead(d) {
  const m = d.meta || {};
  const p = m.profile;
  // One ICTV species can carry several accepted virus names -- Orthobunyavirus
  // catqueense is Cat Que virus AND Oya virus -- so show them all. Showing
  // only the first meant searching "OYAV" landed on a page headed "Cat Que
  // virus", which reads as the wrong record.
  const names = p?.names || [];
  const tierInfo = TIERS[m.tier];
  const spec = d.morphology;

  const kicker = [m.family, m.serogroup, m.clade].filter(Boolean).join(' · ');

  return `
    <header class="hero" data-tier="${esc(m.tier || 'no-evidence')}">
      <div class="crumbs">${crumbs(d.path)}</div>
      <div class="hero-grid">
        <div class="hero-text">
          ${kicker ? `<p class="kicker">${esc(kicker)}</p>` : ''}
          <h2 class="binomial">${esc(d.name)}</h2>
          ${names.length ? `<p class="detail-common">${esc(names[0])}</p>` : ''}
          ${names.length > 1 ? `<p class="detail-synonyms">
              <span>also</span>${names.slice(1).map(nm =>
                `<b>${esc(nm)}</b>`).join('<i>\u00b7</i>')}</p>` : ''}
          <div class="badges">
            ${tierBadge(m.tier)}
            ${m.genome ? `<span class="badge">${esc(m.genome)}</span>` : ''}
            ${spec ? `<span class="badge">${esc(spec.shape_label)}</span>` : ''}
          </div>
          <div class="host-strip">${F.hostStrip(m.hosts)}</div>
          ${p?.headline ? `<p class="headline">${esc(p.headline)}</p>` : ''}
          ${tierInfo ? `<p class="tier-note">${esc(tierInfo.note)}</p>` : ''}
          ${tierProvenance(d, m)}
        </div>
        ${spec ? `<div class="hero-art">${F.virionFigure(spec)}</div>` : ''}
      </div>
    </header>`;
}

/** The figure plate: what this virus looks like, how it spreads, where it is. */
function speciesPlates(d) {
  const m = d.meta || {};
  const p = m.profile;
  const spec = d.morphology;
  let out = '';

  if (spec) {
    out += figure(F.genomeFigure(spec), 'Genome organisation.',
      `${spec.note}${spec.confident ? '' :
        ' Architecture shown is generalised from the genome type — this family has no specific entry in the atlas.'}`,
      'wide');
  }

  if (p && (p.transmission || p.vectors?.length)) {
    out += figure(F.transmissionFigure(p, m), 'Transmission cycle.',
      `${p.transmission} Drawn from the recorded vectors and reservoir; a schematic of the principal route, not every documented pathway.`,
      'wide');
  }

  if (d.geo && (d.geo.countries.length || d.geo.eradicated)) {
    const g = d.geo;
    const svg = g.eradicated
      ? `<div class="map-eradicated"><strong>Eradicated.</strong>
           No natural distribution — the virus exists only in two WHO-authorised repositories.</div>`
      : `<div class="map-slot" data-map='${esc(JSON.stringify(g.countries))}'
              data-worldwide="${g.worldwide ? '1' : '0'}">
           <div class="map-loading">loading map…</div></div>`;
    out += figure(svg, 'Reported distribution.',
      `${g.text}${g.eradicated ? '' :
        ` Countries shaded where the literature reports the virus; resolved from that description, so it is a schematic of reported range rather than a surveillance map.`}`,
      'wide');
  }

  return out ? `<div class="plates">${out}</div>` : '';
}


/* ------------------------------------------------- virology data blocks */

/** Baltimore group: strategy, which ICTV rank does not describe. */
function baltimoreBlock(b) {
  if (!b) return '';
  if (b.unassigned) {
    return section('Baltimore group',
      `<p class="muted">${esc(b.note)}</p>`);
  }
  return section('Baltimore group', `
    <div class="balt">
      <span class="balt-roman">${esc(b.roman)}</span>
      <div class="balt-body">
        <h4>${esc(b.name)}</h4>
        <p>${esc(b.strategy)}</p>
        <p class="muted"><i>Also in this group:</i> ${esc(b.examples)}.</p>
        ${b.note ? `<p class="muted">${esc(b.note)}</p>` : ''}
      </div>
    </div>`);
}

/** Receptor use, which explains tropism better than anything else here. */
function receptorBlock(r) {
  if (!r) return '';
  const list = (label, items) => items?.length
    ? `<div class="rc-row"><i>${label}</i><div>${items.map(x =>
        `<span class="pill">${esc(x)}</span>`).join('')}</div></div>` : '';
  return section('Receptor & cell tropism', `
    ${list('Entry receptor', r.receptors)}
    ${list('Attachment factor', r.attachment)}
    ${r.tropism ? `<div class="rc-row"><i>Tropism</i><p>${esc(r.tropism)}</p></div>` : ''}
    ${r.entry ? `<div class="rc-row"><i>Entry route</i><p>${esc(r.entry)}</p></div>` : ''}
    ${r.note ? `<p class="rc-note">${esc(r.note)}</p>` : ''}`);
}

/** Containment. Jurisdictional and procedure-dependent, so it says so. */
function biosafetyBlock(b) {
  if (!b) return '';
  const BASIS = {
    species: 'Assigned for this species.',
    family: `Family-level default for ${b.family || 'this family'} — no species-specific entry.`,
    'host-range': 'Inferred from ICTV host range.',
  };
  return section('Biosafety & containment', `
    <div class="bsl" data-bsl="${b.bsl}">
      <span class="bsl-badge">${esc(b.bsl_label || '')}</span>
      <div class="bsl-body">
        <p>${esc(b.bsl_practice || '')}</p>
        ${b.bsl_note ? `<p>${esc(b.bsl_note)}</p>` : ''}
        ${b.risk_group_label ? `<p class="muted">${esc(b.risk_group_label)}</p>` : ''}
        ${b.select_agent ? `<p class="bsl-sa">${esc(b.select_agent)}</p>` : ''}
        ${b.vaccine_offer ? `<p class="bsl-vax">${esc(b.vaccine_offer)}</p>` : ''}
        <p class="muted bsl-caveat">${esc(BASIS[b.basis] || '')}
          Containment is jurisdictional and depends on the procedure, not only
          the agent. Orientation only — not a substitute for a local risk
          assessment.</p>
      </div>
    </div>`);
}

/** Vaccines and antivirals, including the explicit absence of them. */
function countermeasureBlock(c) {
  if (!c) return '';
  const group = (label, items, cls) => items?.length
    ? `<div class="cm-group"><i>${label}</i><ul class="${cls}">${items.map(x =>
        `<li>${esc(x)}</li>`).join('')}</ul></div>` : '';
  const none = !c.any;
  return section('Vaccines & antivirals', `
    ${none ? '<p class="cm-none">Nothing licensed.</p>' : ''}
    ${group('Vaccines', c.vaccines, 'cm-list')}
    ${group('Antivirals', c.antivirals, 'cm-list')}
    ${group('Pre- and post-exposure', c.prophylaxis, 'cm-list')}
    ${c.note ? `<p class="cm-note">${esc(c.note)}</p>` : ''}
    <p class="muted cm-caveat">Licensed somewhere is not available everywhere.
      Educational summary, not a formulary and not clinical guidance.</p>`);
}

/** Serological cross-reactivity: why serology in this group misleads. */
function crossreactBlock(list) {
  if (!list?.length) return '';
  return section('Serological cross-reactivity', list.map(c => `
    <div class="xr">
      <h4>${esc(c.name)} <span class="xr-extent">${esc(c.extent)}</span></h4>
      <p><i>Basis.</i> ${esc(c.basis)}</p>
      <p><i>Effect on interpretation.</i> ${esc(c.effect)}</p>
      <p><i>What resolves it.</i> ${esc(c.resolution)}</p>
      ${c.aside ? `<p class="muted">${esc(c.aside)}</p>` : ''}
    </div>`).join(''));
}

/** Syndrome chips, each a link into the differential view. */
function syndromeBlock(list) {
  if (!list?.length) return '';
  return section('Presentations indexed for this virus', `
    <div class="pills">${list.map(sx =>
      `<button class="pill pill-link" type="button" data-syndrome="${esc(sx.key)}"
               title="Matched on &ldquo;${esc(sx.matched || '')}&rdquo; — open the differential for this presentation"
        >${esc(sx.label)}</button>`).join('')}</div>
    <p class="muted">Derived by matching the prose above against syndrome
      keywords, so this is what the text says, not a clinical ranking.</p>`);
}


/**
 * Antiviral therapy with its evidence.
 *
 * Ordered by how good the evidence is rather than by how widely the drug is
 * used, which puts the honest cases in view: remdesivir and molnupiravir as
 * conflicting, tecovirimat as having failed its randomised trials, ribavirin
 * for Lassa as resting on a study since criticised. Every clinical claim
 * carries a PMID, and all of them are machine-verified against Europe PMC by
 * `python -m atlas.update --check-refs`.
 */
function therapeuticsBlock(t) {
  if (!t) return '';
  const nct = ids => (ids || []).map(id =>
    /^NCT/.test(id)
      ? `<a href="https://clinicaltrials.gov/study/${esc(id)}" target="_blank" rel="noopener">${esc(id)}</a>`
      : `<span>${esc(id)}</span>`).join(' · ');
  const refs = rs => (rs || []).map(r =>
    `<li><a href="https://europepmc.org/article/MED/${esc(r.pmid)}" target="_blank" rel="noopener">${esc(r.label)}</a>
         <span class="th-pmid">PMID ${esc(r.pmid)}</span></li>`).join('');

  const agents = (t.agents || []).map(a => `
    <div class="th-agent" data-grade="${esc(a.grade)}">
      <div class="th-head">
        <h4>${esc(a.drug)}</h4>
        <span class="th-grade" title="${esc(a.grade_note || '')}">${esc(a.grade_label || '')}</span>
        <span class="th-status">${esc(a.status)}</span>
      </div>
      ${a.class && a.class !== '—' ? `<p class="th-class">${esc(a.class)}</p>` : ''}
      ${a.use ? `<p><i>Use.</i> ${esc(a.use)}</p>` : ''}
      ${a.evidence ? `<p><i>Evidence.</i> ${esc(a.evidence)}</p>` : ''}
      ${a.trials?.length ? `<p class="th-trials"><i>Trials.</i> ${nct(a.trials)}</p>` : ''}
      ${a.refs?.length ? `<ul class="th-refs">${refs(a.refs)}</ul>` : ''}
    </div>`).join('');

  const inv = (t.investigational || []).map(i => `
    <div class="th-inv">
      <h4>${esc(i.drug)} ${i.class ? `<span class="th-class">${esc(i.class)}</span>` : ''}</h4>
      <p>${esc(i.note)}</p>
      ${i.trials?.length ? `<p class="th-trials"><i>Trials.</i> ${nct(i.trials)}</p>` : ''}
      ${i.refs?.length ? `<ul class="th-refs">${refs(i.refs)}</ul>` : ''}
    </div>`).join('');

  const guides = (t.guidelines || []).map(g =>
    `<li><b>${esc(g.body)}</b> <a href="${esc(g.url)}" target="_blank" rel="noopener">${esc(g.title)}</a></li>`).join('');

  return section('Antiviral therapy & evidence', `
    ${guides ? `<div class="th-guides"><i>Current guidance</i><ul>${guides}</ul></div>` : ''}
    ${t.any_licensed_antiviral ? '' :
      '<p class="cm-none">No licensed antiviral. Any vaccine or immunoprophylaxis is listed separately under Vaccines &amp; antivirals.</p>'}
    ${agents || '<p class="cm-none">No agent with human efficacy evidence.</p>'}
    ${inv ? `<div class="th-invgroup"><i>Investigational &amp; possible agents</i>${inv}</div>` : ''}
    ${t.note ? `<p class="th-note">${esc(t.note)}</p>` : ''}
    <p class="muted th-caveat">Doses are omitted deliberately: this is not a
      prescribing resource. Evidence grades are coarse, licensing differs by
      country, and the linked guidelines are the authority. Every clinical
      claim here carries a PMID, and all of them resolve against Europe PMC —
      which says the paper exists and is cited correctly, not that it proves
      the claim.</p>`);
}

function speciesBody(d) {
  const m = d.meta || {};
  const p = m.profile;

  let body = '';
  if (p) {
    body += section('Clinical syndrome', para(p.syndrome));
    body += section('Transmission & ecology', para(p.transmission) + facts([
      ['Vectors', p.vectors],
      ['Reservoir / host', p.reservoir],
      ['Distribution', p.geography],
      ['Incubation', p.incubation],
    ]));
    body += section('Diagnosis', para(p.diagnosis));
    body += section('Management', para(p.management));
    body += section('Prevention', para(p.prevention));
    if (p.evidence?.length) {
      body += section('Evidence for human infection',
        `<ul class="evidence">${p.evidence.map(e => `<li><span>${esc(e)}</span></li>`).join('')}</ul>`);
    }
    body += section('Key references', refList(p.refs));
    if (p.names?.length > 1) {
      body += section('Also known as',
        `<div class="pills">${p.names.map(n => `<span class="pill">${esc(n)}</span>`).join('')}</div>`);
    }
  } else {
    body += section('Human pathogenicity', `
      <p>No curated human-pathogenicity profile exists for this species in the atlas.
      ICTV records its host source as <strong>${esc(m.host || 'unspecified')}</strong>.
      Absence of a profile means the atlas has no evidence on record — it is not a
      statement that the virus cannot infect humans. The live lookup below searches
      the primary literature for this virus by name.</p>`);
  }

  body += therapeuticsBlock(d.therapeutics);
  body += receptorBlock(d.receptors);
  body += countermeasureBlock(d.countermeasures);
  body += crossreactBlock(d.crossreact);
  body += biosafetyBlock(d.biosafety);
  body += syndromeBlock(d.syndromes);

  if (d.id) body += livePlaceholder(d.id);

  body += baltimoreBlock(d.baltimore);
  body += section('Classification', facts([
    ['Species', d.name],
    ['Genus', m.genus],
    ['Family', m.family],
    ['Serogroup', m.serogroup || 'not assigned in this atlas'],
    ['Antigenic clade', m.clade],
    ['Genome', m.genome],
    ['Host source (ICTV)', m.host],
  ]));

  body += section(
    `Isolates in the ICTV reference set (${(d.isolates || []).length})`,
    isolateTable(d.isolates));

  return body;
}

/* ------------------------------------------------- live evidence lookup */

// Each render gets a token; a slow lookup for a species you have already
// navigated away from is discarded instead of landing in the wrong panel.
let liveToken = 0;

function livePlaceholder(nodeId) {
  return `<section class="section live" data-live="${esc(nodeId)}">
      <h3>Live evidence <span class="live-src">Europe PMC</span></h3>
      <p class="live-status">Searching the literature…</p>
    </section>
    <section class="section genomic" data-genomic="${esc(nodeId)}" hidden></section>`;
}

/**
 * Nextstrain builds for this species, if any.
 *
 * The tree itself is not drawn here. The radial view in this app is a
 * taxonomy -- ICTV ranks, no branch lengths -- and Nextstrain's builds are
 * real time-resolved phylogenies maintained by people who rebuild them daily.
 * Drawing a copy would either be out of date or imply this app had inferred
 * it. So this block reports the build's size, date and composition, and links
 * out.
 */
async function loadGenomic(nodeId) {
  const host = el.side.querySelector(`[data-genomic="${nodeId}"]`);
  if (!host) return;
  let d;
  try {
    d = await api('/api/genomic', { id: nodeId, summary: '1' });
  } catch {
    return;                                   // silent: it is supplementary
  }
  if (!d.summaries?.length) return;
  const rows = d.summaries.map(s => {
    if (s.state === 'failed') {
      return `<li class="gb"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.prefix)}</a>
                <span class="gb-meta">could not be read just now</span></li>`;
    }
    const clades = (s.clades || []).slice(0, 5)
      .map(c => `${esc(c.name)} <b>${c.n}</b>`).join(' · ');
    const places = (s.countries || []).slice(0, 5)
      .map(c => `${esc(c.name)} <b>${c.n}</b>`).join(' · ');
    return `<li class="gb">
        <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>
        <span class="gb-meta">
          <b>${(s.genomes || 0).toLocaleString()}</b> genomes
          ${s.updated ? `· build updated ${esc(s.updated)}` : ''}
          ${s.state === 'stale' ? '· cached copy, refresh failed' : ''}
        </span>
        ${clades ? `<span class="gb-row"><i>clades</i> ${clades}</span>` : ''}
        ${places ? `<span class="gb-row"><i>most sequenced</i> ${places}</span>` : ''}
      </li>`;
  }).join('');
  host.innerHTML = `
    <h3>Genomic epidemiology <span class="live-src">Nextstrain</span></h3>
    <p class="gb-note">
      Live, continuously rebuilt phylogenies for this virus. These are real
      time-resolved trees over public sequence data — unlike the radial view
      here, which is ICTV taxonomy and carries no branch lengths. Opens on
      nextstrain.org.
    </p>
    <ul class="gb-list">${rows}</ul>`;
  host.hidden = false;
}

function paperList(lit) {
  const papers = lit.papers || [];
  if (!papers.length) {
    return `<p>Europe PMC returned no publications for
      ${esc((lit.terms || []).join(' / '))}.</p>`;
  }
  const items = papers.map((p, i) => {
    const links = [];
    if (p.doi) links.push(`<a href="https://doi.org/${esc(encodeURI(p.doi))}" target="_blank" rel="noopener">doi</a>`);
    if (p.pmid) links.push(`<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(p.pmid)}/" target="_blank" rel="noopener">PMID ${esc(p.pmid)}</a>`);
    if (p.pmcid) links.push(`<a href="https://europepmc.org/article/PMC/${encodeURIComponent(p.pmcid)}" target="_blank" rel="noopener">full text</a>`);
    const meta = [p.journal, p.year, p.citations != null ? `cited ${p.citations}` : null]
      .filter(Boolean).join(' · ');
    return `<li class="paper" data-focus="${esc(p.focus)}">
        <span class="ref-n">${i + 1}</span>
        <div>
          <div class="paper-title">${esc(p.title)}</div>
          <div class="paper-meta">${esc(meta)}
            ${p.mentions_human ? '<span class="flag-human">human infection</span>' : ''}
            ${p.focus === 'weak' ? '<span class="flag-weak">passing mention</span>' : ''}
          </div>
          ${p.abstract ? `<details class="paper-abs"><summary>abstract</summary><p>${esc(p.abstract)}</p></details>` : ''}
          ${links.length ? `<div class="ref-links">${links.join('')}</div>` : ''}
        </div>
      </li>`;
  });
  return `<ul class="papers">${items.join('')}</ul>`;
}

function renderLive(host, data) {
  const lit = data.literature || {};
  if (lit.error) {
    host.innerHTML = `<h3>Live evidence</h3>
      <p class="live-status">Literature lookup failed: ${esc(lit.error)}
      <button class="link" type="button" data-retry>retry</button></p>`;
    return;
  }
  const summary = `${lit.total?.toLocaleString() ?? 0} publication${lit.total === 1 ? '' : 's'} match${lit.total === 1 ? 'es' : ''}
    ${esc((lit.terms || []).join(' / '))} — showing ${lit.shown ?? 0},
    of which <strong>${lit.focused ?? 0}</strong> name this virus in the title or
    abstract and <strong>${lit.human_mentions ?? 0}</strong> discuss human infection.`;

  host.innerHTML = `
    <h3>Live evidence
      <span class="live-src">Europe PMC</span>
    </h3>
    <p class="live-summary">${summary}</p>
    ${paperList(lit)}
    <p class="live-foot">
      ${data.cached ? 'Served from local cache' : 'Fetched just now'},
      ${esc((data.fetched_at || '').replace('T', ' ').replace('+00:00', ' UTC'))}.
      <button class="link" type="button" data-retry>refresh</button>
    </p>`;
}

async function loadLive(nodeId, token) {
  const host = el.side.querySelector(`[data-live="${nodeId}"]`);
  if (!host) return;
  try {
    const data = await api('/api/evidence', { id: nodeId });
    if (token !== liveToken) return;            // user navigated away
    renderLive(host, data);
  } catch (err) {
    if (token !== liveToken) return;
    host.innerHTML = `<h3>Live evidence</h3>
      <p class="live-status">Lookup failed: ${esc(err.message)}
      <button class="link" type="button" data-retry>retry</button></p>`;
  }
}

async function refreshLive(host) {
  const nodeId = host.dataset.live || host.closest('.live')?.dataset.live;
  const target = el.side.querySelector(`[data-live="${nodeId}"]`);
  target.innerHTML = '<h3>Live evidence</h3><p class="live-status">Refreshing…</p>';
  const token = ++liveToken;
  const data = await api('/api/evidence', { id: nodeId, refresh: 1 });
  if (token === liveToken) renderLive(target, data);
}

/** An isolate has no pathogenicity record of its own: show its own facts, then
 *  the full briefing for the species it belongs to. */
function isolateDetail(d) {
  figN = 0;
  const m = d.meta || {};
  const sp = d.species;
  const spm = sp?.meta || {};
  const p = spm.profile;
  const spec = d.morphology;

  const head = `
    <header class="hero" data-tier="${esc(spm.tier || 'no-evidence')}">
      <div class="crumbs">${crumbs(d.path)}</div>
      <div class="hero-grid">
        <div class="hero-text">
          <p class="kicker">isolate${m.exemplar ? ' · ICTV exemplar' : ''}</p>
          <h2>${esc(d.name)}</h2>
          ${m.abbrev?.length ? `<p class="detail-common">${esc(m.abbrev.join(' · '))}${
            m.designation ? ` · strain ${esc(m.designation)}` : ''}</p>` : ''}
          <div class="badges">
            ${tierBadge(spm.tier)}
            ${spm.serogroup ? `<span class="badge accent">${esc(spm.serogroup)}</span>` : ''}
            ${m.genome ? `<span class="badge">${esc(m.genome)}</span>` : ''}
            ${m.coverage ? `<span class="badge">${esc(m.coverage)}</span>` : ''}
          </div>
          <p class="tier-note">
            One sequenced isolate from the ICTV reference set. Clinical and
            pathogenicity information is held at species level — the briefing
            below is for
            <button class="link" type="button" data-goto="${esc(sp?.id || '')}"><span class="binomial">${esc(sp?.name || '')}</span></button>.
          </p>
          ${p?.headline ? `<p class="headline">${esc(p.headline)}</p>` : ''}
        </div>
        ${spec ? `<div class="hero-art">${F.virionFigure(spec)}</div>` : ''}
      </div>
    </header>`;

  const plates = sp ? speciesPlates({ id: sp.id, meta: sp.meta, morphology: spec, geo: d.geo }) : '';

  let body = section('This isolate', facts([
    ['Virus name(s)', (m.names || []).join('; ')],
    ['Abbreviation', (m.abbrev || []).join('; ')],
    ['Isolate designation', m.designation],
    ['Genome coverage', m.coverage],
    ['Genome type', m.genome],
    ['Host source (ICTV)', m.host],
  ]) + `<div class="facts" style="margin-top:12px">
      <div class="fact"><dt>GenBank accessions</dt><dd>${accessionLinks(m.accession)}</dd></div>
      ${m.ictv_url ? `<div class="fact"><dt>ICTV record</dt>
        <dd><a href="${esc(m.ictv_url)}" target="_blank" rel="noopener">${esc(m.ictv_url)}</a></dd></div>` : ''}
    </div>`);

  if (sp) {
    body += speciesBody({ id: sp.id, name: sp.name, meta: sp.meta, isolates: sp.isolates });
  }

  body += crossreactBlock(d.crossreact);

  return head + plates + `<div class="sections">${body}</div>`;
}

function groupDetail(d) {
  const total = d.n_species || 0;
  const note = d.note;
  const kids = d.children || [];
  const hl = d.highlights || [];

  figN = 0;
  // A family or genus has one characteristic particle, so it gets the same
  // schematic a species would -- it is the family trait being illustrated.
  const spec = d.morphology;

  const head = `
    <header class="hero hero-group" data-tier="${esc(d.top_tier || 'no-evidence')}">
      <div class="crumbs">${crumbs(d.path)}</div>
      <div class="hero-grid">
        <div class="hero-text">
          <p class="kicker">${esc(d.rank)}</p>
          <h2${isBinomial(d.name, d.rank) ? ' class="binomial"' : ''}>${esc(d.name)}</h2>
          <div class="badges">
            <span class="badge">${total.toLocaleString()} species</span>
            ${tierBadge(d.top_tier && d.top_tier !== 'no-evidence' ? d.top_tier : null)}
            ${spec ? `<span class="badge">${esc(spec.shape_label)}</span>` : ''}
          </div>
          ${note ? `<p class="headline">${esc(note)}</p>` : ''}
          ${distribution(d.tiers || {}, total)}
        </div>
        ${spec ? `<div class="hero-art">${F.virionFigure(spec)}</div>` : ''}
      </div>
    </header>`;

  const plates = spec
    ? `<div class="plates">${figure(F.genomeFigure(spec),
        'Genome organisation.', spec.note, 'wide')}</div>`
    : '';

  let body = '';

  if (hl.length) {
    body += section('Species with human-pathogenicity evidence', `<div class="rows">${
      hl.map(h => rowButton({
        id: h.id,
        name: h.name,
        sub: [h.common, h.serogroup].filter(Boolean).join(' · ') || h.headline,
        meta: TIERS[h.tier]?.label.replace(' human pathogen', ''),
        tier: h.tier,
        italic: true,
      })).join('')}</div>`);
  }

  if (kids.length) {
    const label = kids[0].rank === 'serogroup' ? 'Serogroups' :
                  kids[0].rank === 'clade' ? 'Antigenic clades' :
                  kids[0].rank === 'species' ? 'Species' :
                  `Contains (${kids[0].rank})`;
    body += section(`${label} — ${kids.length}`, `<div class="rows">${
      kids.slice(0, 300).map(k => rowButton({
        id: k.id,
        name: k.name,
        sub: k.common || (k.rank === 'species' ? null : k.rank),
        meta: k.rank === 'species'
          ? (k.n_isolates > 1 ? `${k.n_isolates} isolates` : '')
          : `${(k.n_species || 0).toLocaleString()} sp.`,
        tier: k.rank === 'species' ? k.tier : k.top_tier,
        italic: isBinomial(k.name, k.rank),
      })).join('')}</div>
      ${kids.length > 300 ? `<p style="margin-top:10px">Showing the first 300 of ${kids.length}. Use the tree or search for the rest.</p>` : ''}`);
  }

  return head + plates + `<div class="sections">${body}</div>`;
}

/** The world map is 129 KB, so it loads once on first use and is reused. */
async function mountMaps() {
  const slots = [...el.side.querySelectorAll('.map-slot')];
  if (!slots.length) return;
  try {
    const w = await F.world();
    slots.forEach(slot => {
      if (!slot.isConnected) return;
      const countries = JSON.parse(slot.dataset.map || '[]');
      slot.innerHTML = F.mapFigure(w, countries, { worldwide: slot.dataset.worldwide === '1' });
    });
  } catch (err) {
    slots.forEach(s => { s.innerHTML = `<p class="map-loading">Map unavailable: ${esc(err.message)}</p>`; });
  }
}

/** Repaint the tier dot on any tree row a correction just changed. */
function repaintTiers(chain) {
  (chain || []).forEach(({ id, top_tier }) => {
    const node = nodeEls.get(id);
    if (!node) return;
    const dot = node.querySelector(':scope > .tree-row .dot');
    if (dot) dot.dataset.tier = top_tier || 'unassessed';
  });
}

let detail = null;              // the node currently shown in the side panel

async function showDetail(id) {
  el.side.innerHTML = '<div class="side-empty"><p>Loading…</p></div>';
  const d = await api('/api/node', { id });
  const render = d.rank === 'species' ? speciesDetail
                : d.rank === 'isolate' ? isolateDetail
                : groupDetail;
  detail = d;
  el.side.innerHTML = `<div class="detail">${render(d)}</div>`;
  mountMaps();
  const live = el.side.querySelector('[data-live]');
  if (live) loadLive(live.dataset.live, ++liveToken);
  const gen = el.side.querySelector('[data-genomic]');
  if (gen) loadGenomic(gen.dataset.genomic);
  el.side.scrollTop = 0;
}

el.side.addEventListener('click', ev => {
  const btn = ev.target.closest('[data-goto]');
  if (btn) gotoVirus(btn.dataset.goto);
  const seed = ev.target.closest('[data-seed]');
  if (seed) gotoVirus(SEED);
  const retry = ev.target.closest('[data-retry]');
  if (retry) refreshLive(retry.closest('.live'));

  // --- the tier correction control ---
  const open = ev.target.closest('[data-correct]');
  if (open) {
    const prov = open.closest('.prov');
    const existing = prov.querySelector('.correct');
    if (existing) { existing.remove(); open.setAttribute('aria-expanded', 'false'); return; }
    prov.insertAdjacentHTML('beforeend', correctionForm(detail, detail.meta || {}));
    open.setAttribute('aria-expanded', 'true');
    prov.querySelector('select')?.focus();
  }
  const cancel = ev.target.closest('[data-cancel]');
  if (cancel) {
    const prov = cancel.closest('.prov');
    prov.querySelector('.correct')?.remove();
    prov.querySelector('.prov-head')?.setAttribute('aria-expanded', 'false');
  }
  const revert = ev.target.closest('[data-revert]');
  if (revert) saveCorrection(revert.closest('.correct'), { clear: true });
});

el.side.addEventListener('submit', ev => {
  const form = ev.target.closest('.correct');
  if (!form) return;
  ev.preventDefault();
  saveCorrection(form);
});

/**
 * Persist a tier correction, then reload the node so the badge, the hero
 * colour and every ancestor's rolled-up tier all reflect it. Reloading rather
 * than patching the DOM keeps one source of truth: the server.
 */
async function saveCorrection(form, { clear = false } = {}) {
  const id = form.dataset.id;
  const msg = form.querySelector('.correct-msg');
  const buttons = [...form.querySelectorAll('button')];
  buttons.forEach(b => (b.disabled = true));
  msg.textContent = clear ? 'Removing…' : 'Saving…';
  msg.className = 'correct-msg';
  try {
    // Resolved like every other call here, against the document base.
    const url = new URL('api/tier', document.baseURI);
    let res;
    if (clear) {
      url.searchParams.set('id', id);
      res = await fetch(url, { method: 'DELETE' });
    } else {
      res = await fetch(url, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          id,
          tier: form.elements.tier.value,
          note: form.elements.note.value,
        }),
      });
    }
    if (!res.ok) throw new Error(`${res.status} ${(await res.text()).slice(0, 120)}`);
    const out = await res.json();
    repaintTiers(out.path_tiers);         // the species and every ancestor
    await showDetail(id);                 // redraw from the server's own state
    if (typeof Radial !== 'undefined' && Radial.rootId) {
      Radial.load(Radial.rootId, { animate: false });
    }
  } catch (err) {
    buttons.forEach(b => (b.disabled = false));
    msg.textContent = `Could not save: ${err.message}`;
    msg.className = 'correct-msg is-error';
  }
}

/* -------------------------------------------------------------- search */

let searchTimer, activeIdx = -1, lastResults = [];

function highlight(text, needle) {
  const i = text.toLowerCase().indexOf(needle.toLowerCase());
  if (i < 0) return esc(text);
  return esc(text.slice(0, i)) + '<em>' + esc(text.slice(i, i + needle.length)) +
         '</em>' + esc(text.slice(i + needle.length));
}

function renderResults(data) {
  lastResults = data.results;
  activeIdx = -1;
  if (!data.results.length) {
    el.results.innerHTML = `<div class="results-empty">No match for “${esc(data.q)}”.</div>`;
    el.results.hidden = false;
    return;
  }
  const rows = data.results.map((r, i) => {
    const matched = r.matched.filter(m => m !== r.name);
    const sub = [matched.join(' · '), r.serogroup, r.path.slice(-2).join(' › ')]
      .filter(Boolean).join('  ·  ');
    return `<button class="result" type="button" data-goto="${esc(r.id)}" data-i="${i}">
        <span class="dot" data-tier="${esc(r.tier || 'no-evidence')}"></span>
        <span>
          <span class="result-name">${highlight(r.name, data.q)}</span>
          ${sub ? `<span class="result-sub">${esc(sub)}</span>` : ''}
        </span>
        <span class="result-rank">${esc(r.rank)}</span>
      </button>`;
  });
  const more = data.total > data.results.length
    ? `<div class="results-note">${data.total.toLocaleString()} matches — showing the best ${data.results.length}.</div>`
    : '';
  el.results.innerHTML = rows.join('') + more;
  el.results.hidden = false;
}

el.q.addEventListener('input', () => {
  clearTimeout(searchTimer);
  const q = el.q.value.trim();
  if (q.length < 2) { el.results.hidden = true; return; }
  searchTimer = setTimeout(() => {
    api('/api/search', { q }).then(renderResults).catch(() => { el.results.hidden = true; });
  }, 130);
});

el.q.addEventListener('keydown', ev => {
  if (ev.key === 'Escape') { el.results.hidden = true; el.q.blur(); return; }
  if (el.results.hidden || !lastResults.length) return;
  if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
    ev.preventDefault();
    activeIdx = (activeIdx + (ev.key === 'ArrowDown' ? 1 : -1) + lastResults.length) % lastResults.length;
    el.results.querySelectorAll('.result').forEach((b, i) => b.classList.toggle('active', i === activeIdx));
    el.results.querySelector(`.result[data-i="${activeIdx}"]`)?.scrollIntoView({ block: 'nearest' });
  } else if (ev.key === 'Enter') {
    ev.preventDefault();
    const pick = lastResults[activeIdx >= 0 ? activeIdx : 0];
    if (pick) { el.results.hidden = true; el.q.blur(); select(pick.id, { scroll: true }); }
  }
});


/**
 * Open a virus from anywhere — search, travel, signals, the pathogen index,
 * the radial view — and leave the browser pointing at it.
 *
 * Every source used to call select() with its own options, so some paths
 * expanded and scrolled the tree to the selection and others silently left
 * the tree wherever it was. Routing them all through here means the tree is
 * always moved to whatever you are reading, and whichever overlay you came
 * from gets out of the way first.
 */
function gotoVirus(id, { keepView = false } = {}) {
  if (!id) return;
  el.modal.hidden = true;
  el.results.hidden = true;
  if (!keepView && !isView('tree')) setView('tree');
  // The tree cannot be revealed while it is collapsed.
  document.querySelector('.layout').classList.remove('tree-hidden');
  select(id, { scroll: true });
}

el.results.addEventListener('click', ev => {
  const btn = ev.target.closest('[data-goto]');
  if (btn) gotoVirus(btn.dataset.goto);
});

document.addEventListener('click', ev => {
  if (!ev.target.closest('.search')) el.results.hidden = true;
});

document.addEventListener('keydown', ev => {
  if (ev.key === '/' && document.activeElement !== el.q) {
    ev.preventDefault(); el.q.focus(); el.q.select();
  }
  if (ev.key === 'Escape' && !el.modal.hidden) { el.modal.hidden = true; return; }
  if (ev.key === 'Escape' && !isView('tree')) setView('tree');
});

/* --------------------------------------------------------- pathogen index */

let pathogenData = null;

// 400-odd entries is too many to scan, so the index filters as you type and
// can be narrowed to the species carrying a full write-up.
function renderPathogens(q = '', profiledOnly = false) {
  const data = pathogenData;
  const needle = q.trim().toLowerCase();
  const match = s => {
    if (profiledOnly && !s.profiled) return false;
    if (!needle) return true;
    return [s.name, s.common, s.family, s.genus, s.serogroup]
      .some(v => v && v.toLowerCase().includes(needle));
  };
  let shown = 0;
  const blocks = Object.entries(data.tiers)
    .map(([tier, list]) => [tier, list.filter(match)])
    .filter(([, list]) => list.length)
    .map(([tier, list]) => {
      shown += list.length;
      return `
      <div class="tier-block">
        <header><span class="dot" data-tier="${tier}"></span>
          <h3>${esc(data.legend[tier].label)}</h3>
          <span class="count">${list.length}</span></header>
        <p class="tier-sub">${esc(data.legend[tier].note)}</p>
        <div class="tier-grid">${list.map(s => rowButton({
          id: s.id, name: s.name,
          sub: [s.common, s.serogroup || s.family].filter(Boolean).join(' · '),
          meta: s.profiled ? 'profile' : null,
          tier, italic: true,
        })).join('')}</div>
      </div>`;
    });
  el.modalBody.querySelector('.pix-results').innerHTML = blocks.join('')
    || `<p class="results-note">Nothing matches “${esc(q)}”.</p>`;
  el.modalBody.querySelector('.pix-count').textContent =
    `${shown.toLocaleString()} of ${Object.values(data.tiers)
      .reduce((n, l) => n + l.length, 0).toLocaleString()} species`;
}

document.getElementById('btn-pathogens').addEventListener('click', async () => {
  el.modal.hidden = false;
  document.getElementById('modal-title').textContent = 'Pathogen index';
  el.modalBody.innerHTML = '<p class="results-note">Loading…</p>';
  pathogenData = await api('/api/pathogens');
  el.modalBody.innerHTML = `
    <div class="pix-bar">
      <input class="pix-q" type="search" autocomplete="off" spellcheck="false"
             placeholder="Filter by virus, family or genus — try “herpes”, “Flaviviridae”, “HPV”"
             aria-label="Filter the pathogen index">
      <label class="pix-toggle">
        <input type="checkbox" class="pix-profiled">
        <span>full write-up only</span>
      </label>
      <span class="pix-count"></span>
    </div>
    <p class="pix-note">
      Every species whose evidence tier says something about human infection,
      however that tier was assigned — not only the ones with a long-form
      briefing. Species with no vertebrate host, and species nobody has
      assessed, are left out.
    </p>
    <div class="pix-results"></div>`;
  renderPathogens();
  const q = el.modalBody.querySelector('.pix-q');
  const only = el.modalBody.querySelector('.pix-profiled');
  const update = () => renderPathogens(q.value, only.checked);
  q.addEventListener('input', update);
  only.addEventListener('change', update);
  q.focus();
});

el.modal.addEventListener('click', ev => {
  if (ev.target === el.modal || ev.target.closest('[data-close]')) { el.modal.hidden = true; return; }
  const btn = ev.target.closest('[data-goto]');
  if (btn) gotoVirus(btn.dataset.goto);
});

/* ------------------------------------------------------------- controls */

document.getElementById('btn-theme').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('va-theme', next); } catch (e) { /* private mode */ }
});

try {
  const saved = localStorage.getItem('va-theme');
  if (saved) document.documentElement.dataset.theme = saved;
} catch (e) { /* private mode */ }

let radialReady = false;


/* ----------------------------------------------------------- view state */

/**
 * The left column holds the tree, the radial view or the travel panel, and
 * only ever one of them. These used to be three independent toggles that each
 * hid the others with their own CSS rule, so opening one could strand you in
 * a panel with no visible way back. Now a single data-view attribute decides
 * what is shown, every toolbar button routes through here, and the button
 * states always agree with what is on screen.
 */
const VIEWS = {
  tree: { panel: null, btn: null },
  radial: { panel: 'radialPanel', btn: 'btn-radial' },
  travel: { panel: 'travelPanel', btn: 'btn-travel' },
  dx: { panel: 'dxPanel', btn: 'btn-dx' },
};
let view = 'tree';

function setView(next) {
  if (!VIEWS[next]) next = 'tree';
  view = next;
  const layout = document.querySelector('.layout');
  layout.dataset.view = next;
  // Leaving the tree view also cancels "tree hidden", or the left column
  // would end up empty.
  if (next !== 'tree') layout.classList.remove('tree-hidden');
  for (const [name, cfg] of Object.entries(VIEWS)) {
    if (cfg.panel) el[cfg.panel].hidden = name !== next;
    if (cfg.btn) {
      document.getElementById(cfg.btn)
        .setAttribute('aria-pressed', String(name === next));
    }
  }
  if (next === 'radial') openRadial();
  if (next === 'travel') openTravel();
  if (next === 'dx') openDx();
}

const isView = name => view === name;

function setRadial(on) {
  setView(on ? 'radial' : 'tree');
}

function openRadial() {
  if (!radialReady) {
    Radial.attach(el.radial, (id, opts) => {
      // Re-rooting shouldn't yank the tree around; reading a tip should move
      // it, and should hand the column back so the tree is visible.
      if (opts?.keepView) select(id, { scroll: false });
      else gotoVirus(id);
    });
    radialReady = true;
  }
  // Open on whatever is selected, at a rank with a readable fan-out.
  const path = ancestryOf(selected);
  Radial.focus(selected || 'root', path);
}

/** Ancestor chain for a node id, derived from the id itself. */
function ancestryOf(id) {
  if (!id) return [];
  const parts = id.split('/');
  const out = [];
  for (let i = 1; i <= parts.length; i++) {
    const pid = parts.slice(0, i).join('/');
    const node = nodeEls.get(pid);
    const row = node?.querySelector(':scope > .tree-row');
    out.push({ id: pid, rank: row?.dataset.rank || (i === 1 ? 'root' : ''),
               name: row?.querySelector('.tree-name')?.textContent || '' });
  }
  return out;
}

document.getElementById('btn-radial').addEventListener('click', () => {
  setRadial(el.radialPanel.hidden);
});
document.getElementById('btn-radial-close').addEventListener('click', () => setRadial(false));

document.getElementById('btn-tree').addEventListener('click', () => {
  // Outside the tree view this button is the way back to it; inside it, it
  // collapses the tree so the article gets the full width.
  if (!isView('tree')) { setView('tree'); return; }
  document.querySelector('.layout').classList.toggle('tree-hidden');
});

document.querySelector('.tree-tools').addEventListener('click', ev => {
  const jump = ev.target.closest('[data-jump]');
  if (jump) { select(jump.dataset.jump, { scroll: true }); return; }
  if (ev.target.closest('[data-collapse]')) {
    document.querySelectorAll('.tree-node.open').forEach(n => {
      if (n.parentElement === el.tree) return;   // keep the realms open
      collapse(n);
    });
  }
});

/* --------------------------------------------------- material + motion */

// Fluent-style reveal: the surface under the pointer lights from the cursor.
// Driven by CSS custom properties so the paint stays on the compositor.
const REVEAL_SEL = '.plate, .row-btn, .paper, .ref, .btn, .chip, .result, .host-chip';

document.addEventListener('pointermove', ev => {
  const t = ev.target.closest?.(REVEAL_SEL);
  if (!t) return;
  if (!t.classList.contains('reveal')) t.classList.add('reveal');
  const b = t.getBoundingClientRect();
  t.style.setProperty('--mx', `${ev.clientX - b.left}px`);
  t.style.setProperty('--my', `${ev.clientY - b.top}px`);
}, { passive: true });

/* ----------------------------------------------------------------- boot */

(async function boot() {
  const meta = await api('/api/meta');
  TIERS = meta.tiers;
  EPHEMERAL = !!(meta.live && meta.live.ephemeral);

  el.legend.innerHTML = Object.entries(TIERS).map(([k, v]) =>
    `<span class="legend-item" title="${esc(v.note)}">
       <span class="dot" data-tier="${k}"></span>${esc(v.label)}
       <b>${(meta.totals.tiers[k] || 0).toLocaleString()}</b></span>`).join('');

  el.treeSub.textContent =
    `${meta.totals.species.toLocaleString()} ICTV species · ` +
    `${meta.totals.profiled} with a pathogenicity profile · ` +
    `serogroups shown in colour`;

  meta.roots.forEach(r => el.tree.appendChild(makeNode(r)));

  // Open on Oya virus: the Simbu-serogroup example that motivated the atlas.
  await select(SEED, { scroll: true });
})();

/* ======================================================================
   Travel exposure, live signals, and genomic builds
   ====================================================================== */

const WINDOW_LABEL = {
  plausible: ['in window', 'The incubation period for this virus covers the time since return.'],
  early: ['too early', 'Shorter than the usual minimum incubation — unlikely to have declared itself yet.'],
  late: ['window passed', 'Longer than the usual maximum incubation — a new illness is unlikely to be this.'],
  unknown: ['no window', 'No incubation period recorded, so time since return cannot filter it.'],
  unfiltered: ['', ''],
};

function travelRow(e) {
  const [wl, wt] = WINDOW_LABEL[e.window] || ['', ''];
  const inc = e.incubation_days
    ? `${e.incubation_days[0]}–${e.incubation_days[1]} d` : null;
  return `
    <button class="trow" type="button" data-goto="${esc(e.id)}"
            data-window="${esc(e.window || '')}">
      <span class="dot" data-tier="${esc(e.tier)}"></span>
      <span class="trow-main">
        <span class="trow-name">${esc(e.common || e.species)}</span>
        <span class="trow-sp">${esc(e.species)}</span>
        ${e.headline ? `<span class="trow-sub">${esc(e.headline.slice(0, 160))}</span>` : ''}
      </span>
      <span class="trow-meta">
        ${inc ? `<span class="trow-inc">${esc(inc)}</span>` : ''}
        ${wl ? `<span class="trow-win" title="${esc(wt)}">${esc(wl)}</span>` : ''}
        ${e.routes_inherited ? '<span class="trow-inf" title="Exposure route inferred from other species in the same genus, not from a profile for this virus">inferred route</span>' : ''}
        ${e.evidence && e.evidence !== 'human' ? `<span class="trow-ev" data-ev="${esc(e.evidence)}" title="${esc(e.evidence_note || '')}">${esc(e.evidence_label || '')}</span>` : ''}
        ${e.geo_inferred ? `<span class="trow-inf" title="This country was not named for this virus. It was inferred by expanding the region “${esc(e.geo_region || '')}”, so it may be wider than the real range.">via ${esc(e.geo_region || 'region')}</span>` : ''}
      </span>
    </button>`;
}

function renderTravel(d) {
  const out = document.getElementById('travel-out');
  if (!d.known_country) {
    out.innerHTML = `
      <p class="travel-hint">No country in the index matches
        “${esc(d.asked || d.country || '')}”.
        ${d.suggestions?.length
          ? `Did you mean ${d.suggestions.map(s =>
              `<button class="link" type="button" data-country="${esc(s)}">${esc(s)}</button>`
            ).join(', ')}?` : ''}</p>`;
    return;
  }
  const c = d.counts;
  const win = d.days_since_return != null;
  out.innerHTML = `
    <div class="travel-summary">
      <h3>${esc(d.country)}</h3>
      <p class="travel-counts">
        <b>${c.regional}</b> viruses reported from this destination
        <span class="travel-prov">(<b>${c.human_evidence}</b> with human cases
          reported here${c.reservoir_only
            ? `, <b>${c.reservoir_only}</b> found only in reservoir animals or vectors`
            : ''}; ${d.regional.filter(r => r.geo_inferred).length} inferred
          from a wider region)</span>
        ${win ? `· <b>${c.plausible}</b> still within their incubation window
                 at day ${d.days_since_return}
                 · ${c.late} window passed · ${c.early} too early
                 · ${c.unknown_window} no window recorded` : ''}
      </p>
    </div>

    ${d.signals?.length ? `
      <div class="travel-block travel-live">
        <h4>Currently being reported there</h4>
        <p class="travel-note">WHO Disease Outbreak News items naming this
          country. A report means WHO published on an event, not that risk is
          ongoing today.</p>
        <ul class="sig-list">${d.signals.map(s => `
          <li>
            <span class="sig-date">${esc(s.date)}</span>
            ${s.node ? `<button class="link" type="button" data-goto="${esc(s.node)}">${esc(s.disease)}</button>`
                     : `<b>${esc(s.disease || '')}</b>`}
            <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>
          </li>`).join('')}</ul>
      </div>` : ''}

    ${d.groups.map(g => `
      <div class="travel-block">
        <h4>${esc(g.label)} <span class="count">${g.entries.length}</span></h4>
        <div class="trows">${g.entries.map(travelRow).join('')}</div>
      </div>`).join('')}

    ${d.worldwide?.length ? `
      <div class="travel-block travel-cosmo">
        <h4>Everywhere, including home <span class="count">${d.worldwide.length}</span></h4>
        <p class="travel-note">Cosmopolitan viruses, listed separately because
          they are not a reason to suspect the destination.</p>
        <div class="trows">${d.worldwide.map(travelRow).join('')}</div>
      </div>` : ''}

    <p class="travel-caveat">
      <b>Reservoir detection only</b> means the virus has been found in its
      host animal or vector here with no human case ever reported — present in
      the country, but not shown to have infected anyone in it. Nipah virus in
      Sri Lankan <i>Pteropus</i> bats is the type example.
      Entries marked <i>via &lt;region&gt;</i> were not reported for this
      country specifically — they come from expanding a region named in the
      virus' profile, so their range may be wider than the truth.
      Geographical presence in the literature, not a risk assessment: endemic
      range is uneven within a country, much transmission is rural and
      seasonal, and this list reflects what has been curated here. Any acute
      febrile illness after travel needs malaria excluded first — a parasite,
      and outside this atlas. Educational reference only.
    </p>`;
}

async function runTravel() {
  const country = document.getElementById('travel-country').value.trim();
  const days = document.getElementById('travel-days').value.trim();
  if (!country) return;
  const out = document.getElementById('travel-out');
  out.innerHTML = '<p class="travel-hint">Loading…</p>';
  try {
    const params = { country };
    if (days !== '') params.days = days;
    renderTravel(await api('/api/travel', params));
  } catch (err) {
    out.innerHTML = `<p class="travel-hint">Could not load: ${esc(err.message)}</p>`;
  }
}

function setTravel(on) {
  setView(on ? 'travel' : 'tree');
}

function openTravel() {
  if (!el.travelPanel.dataset.ready) {
    el.travelPanel.dataset.ready = '1';
    api('/api/travel').then(d => {
      document.getElementById('travel-countries').innerHTML =
        d.countries.map(c => `<option value="${esc(c)}">`).join('');
    }).catch(() => {});
  }
  document.getElementById('travel-country').focus();
}

document.getElementById('btn-travel').addEventListener('click', () => {
  setView(isView('travel') ? 'tree' : 'travel');
});
document.getElementById('btn-travel-close').addEventListener('click', () => setTravel(false));
document.getElementById('travel-form').addEventListener('submit', ev => {
  ev.preventDefault();
  runTravel();
});
el.travelPanel.addEventListener('click', ev => {
  const pick = ev.target.closest('[data-country]');
  if (pick) {
    document.getElementById('travel-country').value = pick.dataset.country;
    runTravel();
    return;
  }
  const go = ev.target.closest('[data-goto]');
  // Reading about a virus hands the left column back to the tree, pointed at
  // it, rather than leaving you in a panel with no way out.
  if (go) gotoVirus(go.dataset.goto);
});

/* ---------------------------------------------------------- live signals */

document.getElementById('btn-signals').addEventListener('click', async () => {
  el.modal.hidden = false;
  document.getElementById('modal-title').textContent = 'Current outbreak reporting';
  el.modalBody.innerHTML = '<p class="results-note">Loading WHO Disease Outbreak News…</p>';
  let d;
  try {
    d = await api('/api/signals');
  } catch (err) {
    el.modalBody.innerHTML = `<p class="results-note">Could not load: ${esc(err.message)}</p>`;
    return;
  }
  const src = d.sources.map(s => {
    const age = s.fetched_at ? Math.round((Date.now() / 1000 - s.fetched_at) / 60) : null;
    return `${s.source}: ${s.state}${age != null ? `, ${age} min ago` : ''}`;
  }).join(' · ');
  const rows = d.signals.map(s => `
    <li class="sig" data-kind="${esc(s.kind)}">
      <span class="sig-date">${esc(s.date)}</span>
      <span class="sig-body">
        <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>
        ${s.node
          ? `<button class="link" type="button" data-goto="${esc(s.node)}">${esc(s.disease)}</button>`
          : `<span class="sig-tag">${s.kind === 'non-viral' ? 'not a virus' : 'no pathogen named'}</span>`}
      </span>
    </li>`).join('');
  el.modalBody.innerHTML = `
    ${d.ecdc ? `<div class="th-guides"><i>This week in Europe</i><ul><li>
      <b>ECDC</b> <a href="${esc(d.ecdc.url)}" target="_blank" rel="noopener">${esc(d.ecdc.title)}</a>
      <span class="sig-src">PDF, not parsed here \u2014 opens at ecdc.europa.eu</span>
      </li></ul></div>` : ''}
    <p class="pix-note">
      WHO Disease Outbreak News and UK Health Security Agency publications,
      newest first. This is a record of what WHO has
      formally reported — not incidence, and not a complete picture of global
      activity. Reports that name no pathogen, and non-viral events, are kept
      in the list and labelled rather than quietly filtered out. UKHSA is a
      national agency, so its scope is narrower than WHO's: repeated weekly
      series are collapsed to their most recent entry, and series that report
      activity without naming a pathogen are left out.
      <br><span class="sig-src">${esc(src)} · ${d.counts.matched} of
      ${d.counts.total} matched to a virus in this atlas</span>
    </p>
    <ul class="sig-list sig-full">${rows}</ul>`;
});


/* ================================================================
   Differential by presentation
   ================================================================ */

let dxMeta = null;

function openDx() {
  if (!el.dxPanel.dataset.ready) {
    el.dxPanel.dataset.ready = '1';
    api('/api/differential').then(d => {
      dxMeta = d;
      document.getElementById('dx-syndrome').innerHTML = d.syndromes
        .map(s => `<option value="${esc(s.key)}" title="${esc(s.note)}">${esc(s.label)} — ${s.n}</option>`)
        .join('');
      document.getElementById('dx-route').innerHTML = '<option value="">any</option>'
        + d.routes.map(r => `<option value="${esc(r.key)}">${esc(r.label)}</option>`).join('');
      document.getElementById('dx-countries').innerHTML =
        d.countries.map(c => `<option value="${esc(c)}">`).join('');
    }).catch(() => {});
  }
  document.getElementById('dx-syndrome').focus();
}

function dxRow(c) {
  const [wl, wt] = WINDOW_LABEL[c.window] || ['', ''];
  const inc = c.incubation_days ? `${c.incubation_days[0]}–${c.incubation_days[1]} d` : null;
  const routes = (c.routes || []).map(r => ROUTE_SHORT[r] || r).join(' · ');
  return `
    <button class="trow" type="button" data-goto="${esc(c.id)}"
            data-window="${esc(c.window || '')}">
      <span class="dot" data-tier="${esc(c.tier)}"></span>
      <span class="trow-main">
        <span class="trow-name">${esc(c.common || c.species)}</span>
        <span class="trow-sp">${esc(c.species)}</span>
        <span class="trow-sub">matched on &ldquo;${esc(c.phrase || '')}&rdquo;${
          routes ? ` · ${esc(routes)}` : ''}</span>
      </span>
      <span class="trow-meta">
        <span class="trow-score" title="Keyword match strength, weighted by where the term appears in the profile. Not a probability.">${c.score.toFixed(2)}</span>
        ${inc ? `<span class="trow-inc">${esc(inc)}</span>` : ''}
        ${wl ? `<span class="trow-win" title="${esc(wt)}">${esc(wl)}</span>` : ''}
        ${c.scope === 'worldwide'
          ? '<span class="trow-scope" title="Cosmopolitan — present at home as well as at the destination, so not a reason to suspect the travel itself">everywhere</span>'
          : c.scope === 'regional'
            ? '<span class="trow-scope" data-scope="regional" title="Reported from this destination specifically">destination</span>' : ''}
        ${c.evidence && c.evidence !== 'human'
          ? `<span class="trow-ev" data-ev="${esc(c.evidence)}">${esc(c.evidence_label)}</span>` : ''}
      </span>
    </button>`;
}

const ROUTE_SHORT = {
  mosquito: 'mosquito', tick: 'tick', midge: 'midge', sandfly: 'sandfly',
  'faecal-oral': 'food/water', respiratory: 'respiratory',
  'animal-bite': 'animal bite', 'animal-contact': 'animal contact',
  rodent: 'rodent', bat: 'bat', 'bodily-fluid': 'blood/fluids',
  sexual: 'sexual', vertical: 'vertical', unclear: 'route unclear',
};

function renderDx(d) {
  const out = document.getElementById('dx-out');
  if (!d.candidates.length) {
    out.innerHTML = `<p class="travel-hint">Nothing in the index matches
      <b>${esc(d.label)}</b>${d.country ? ` for ${esc(d.country)}` : ''}
      ${d.route ? ` by ${esc(ROUTE_SHORT[d.route] || d.route)}` : ''}.
      ${d.asked_country && !d.known_country
        ? `No country matched &ldquo;${esc(d.asked_country)}&rdquo;.` : ''}
      Of ${d.counts.unfiltered} viruses indexed for this presentation, none
      survived the filters — try removing one.</p>`;
    return;
  }
  out.innerHTML = `
    <div class="travel-summary">
      <h3>${esc(d.label)}</h3>
      <p class="travel-counts">
        <b>${d.counts.total}</b> candidate${d.counts.total === 1 ? '' : 's'}
        ${d.counts.total < d.counts.unfiltered
          ? `, narrowed from ${d.counts.unfiltered} by the filters` : ''}
        ${d.country ? ` · <b>${d.candidates.filter(c => c.scope === 'regional').length}</b>
          reported from <b>${esc(d.country)}</b>,
          ${d.candidates.filter(c => c.scope === 'worldwide').length} cosmopolitan` : ''}
        ${d.days_since_return != null ? ` · day ${d.days_since_return}` : ''}
      </p>
      <p class="travel-note">${esc(d.note)}</p>
    </div>
    <div class="trows">${d.candidates.map(dxRow).join('')}</div>
    <p class="travel-caveat">
      Candidates marked <i>everywhere</i> are cosmopolitan — they are included
      because a returning traveller can have them too, not because of the
      destination. Ranked by how strongly the curated prose matches this presentation, and
      by where in the text it matched — <b>not</b> by probability, prevalence,
      season or vaccination history. A virus is missing if its profile does not
      mention the syndrome, and the atlas contains only viruses: for a febrile
      returning traveller, <b>exclude malaria first</b>. Educational reference
      only, not a diagnostic aid.
    </p>`;
}

async function runDx(preset) {
  const syn = preset || document.getElementById('dx-syndrome').value;
  if (!syn) return;
  const out = document.getElementById('dx-out');
  out.innerHTML = '<p class="travel-hint">Loading…</p>';
  const params = { syndrome: syn };
  const country = document.getElementById('dx-country').value.trim();
  const days = document.getElementById('dx-days').value.trim();
  const route = document.getElementById('dx-route').value;
  if (country) params.country = country;
  if (days !== '') params.days = days;
  if (route) params.route = route;
  try {
    renderDx(await api('/api/differential', params));
  } catch (err) {
    out.innerHTML = `<p class="travel-hint">Could not load: ${esc(err.message)}</p>`;
  }
}

document.getElementById('btn-dx').addEventListener('click', () => {
  setView(isView('dx') ? 'tree' : 'dx');
});
document.getElementById('btn-dx-close').addEventListener('click', () => setView('tree'));
document.getElementById('dx-form').addEventListener('submit', ev => {
  ev.preventDefault();
  runDx();
});
el.dxPanel.addEventListener('click', ev => {
  const go = ev.target.closest('[data-goto]');
  if (go) gotoVirus(go.dataset.goto);
});

// A syndrome chip on a virus page opens the differential for that
// presentation, which is the loop that makes both views worth having.
el.side.addEventListener('click', ev => {
  const chip = ev.target.closest('[data-syndrome]');
  if (!chip) return;
  setView('dx');
  const run = () => {
    const sel = document.getElementById('dx-syndrome');
    if (!sel.options.length) return setTimeout(run, 150);
    sel.value = chip.dataset.syndrome;
    runDx(chip.dataset.syndrome);
  };
  run();
});
