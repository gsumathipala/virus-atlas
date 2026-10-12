/*! Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
 *  Proprietary. No licence granted; see LICENSE. */
/* Virus Atlas — the API, reimplemented in the browser.
 *
 * GitHub Pages serves files, not programs, so there is no Flask to answer
 * /api/... . This intercepts `fetch` for those paths and answers them from
 * the JSON that export_static.py pre-rendered, or by calling the upstream
 * source directly where that source allows cross-origin requests.
 *
 * Intercepting fetch rather than changing the callers is deliberate: app.js
 * and radial.js are identical in both deployments, so the hosted copy cannot
 * drift from the one that runs against the real server.
 *
 * Loaded only by the static build. When it is absent, every call goes to
 * Flask exactly as before.
 *
 * What differs from the server
 * ----------------------------
 *   Tier corrections    kept in localStorage. They persist for this browser
 *                       and are neither shared nor published, because there
 *                       is nothing to write to.
 *   Live lookups        Europe PMC, WHO, gov.uk and Nextstrain are called
 *                       straight from the page; all four send
 *                       access-control-allow-origin: *. Nothing is cached
 *                       between reloads, so a repeat lookup refetches.
 *   ECDC                the one source that cannot be reached: it sends no
 *                       CORS header, so the weekly threat-report link is
 *                       absent from the signals panel here.
 *   Data freshness      the taxonomy is a snapshot taken at build time.
 *
 * Everything else is answered byte-for-byte as Flask answers it; tests/
 * parity.js drives both and diffs them.
 */

(function () {
  'use strict';

  const BASE = new URL('.', document.baseURI).href.replace(/\/$/, '');
  const API = BASE + '/api';
  const OVERRIDES_KEY = 'virus-atlas:overrides';

  /* ------------------------------------------------------------- loading */

  const cache = new Map();
  function load(path) {
    if (!cache.has(path)) {
      cache.set(path, fetch(`${API}/${path}`).then(r => {
        if (!r.ok) throw new Error(`${path}: ${r.status}`);
        return r.json();
      }));
    }
    return cache.get(path);
  }

  /* A synthesized response.
   *
   * Browsers all provide the Response constructor, but depending on it meant
   * the shim could not be exercised outside one -- jsdom has fetch but no
   * Response -- and an untestable compatibility layer is the wrong thing to
   * ship. So: use the real class where it exists, and otherwise return an
   * object carrying the only four members the application reads (ok, status,
   * json, text). */
  const json = (body, status = 200) => {
    const text = JSON.stringify(body);
    if (typeof Response === 'function') {
      return new Response(text, {
        status,
        headers: { 'content-type': 'application/json' },
      });
    }
    return {
      ok: status >= 200 && status < 300,
      status,
      headers: { get: k => (k.toLowerCase() === 'content-type'
        ? 'application/json' : null) },
      json: async () => JSON.parse(text),
      text: async () => text,
    };
  };

  const fold = s => (s || '').toLowerCase()
    .normalize('NFKD').replace(/[̀-ͯ]/g, '');

  const esc = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  /* --------------------------------------------------- node reconstruction */

  let skeleton = null, bundleIndex = null, tables = null;

  async function boot() {
    if (!skeleton) {
      [skeleton, bundleIndex, tables] = await Promise.all([
        load('skeleton.json'), load('bundle-index.json'), load('tables.json'),
      ]);
    }
  }

  /** The family ancestor of an id, by longest prefix present in the index. */
  function familyOf(id) {
    const parts = id.split('/');
    for (let i = parts.length; i > 0; i--) {
      const anc = parts.slice(0, i).join('/');
      if (bundleIndex[anc]) return anc;
    }
    return null;
  }

  async function bundleFor(id) {
    const fam = familyOf(id);
    if (!fam) return null;
    return load(`bundle/${bundleIndex[fam]}.json`);
  }

  /** Ancestry rebuilt from the id, which is itself the path. */
  async function ancestry(id) {
    const parts = id.split('/');
    const out = [];
    for (let i = 1; i <= parts.length; i++) {
      const anc = parts.slice(0, i).join('/');
      const rec = skeleton[anc] || (await nodeRaw(anc));
      if (rec) out.push({ id: anc, name: rec.name, rank: rec.rank });
    }
    return out;
  }

  async function nodeRaw(id) {
    if (skeleton[id]) return skeleton[id];
    const b = await bundleFor(id);
    if (b && b[id]) return b[id];
    // An isolate: its id is its species' id plus /i<index>, and it shares its
    // species' bundle.
    const m = /^(.*)\/i(\d+)$/.exec(id);
    if (!m) return null;
    return isolateRecord((b && b[m[1]]) || await nodeRaw(m[1]), +m[2]);
  }

  /** An isolate node, rebuilt from its species record.
   *
   * Isolates are not exported, and do not need to be: the species record
   * already carries each one's metadata in `isolates`, in index order, and an
   * isolate's name is its first listed name. Writing all 19,285 of them again
   * would have cost megabytes to say nothing new. */
  function isolateRecord(species, index) {
    if (!species || species.rank !== 'species') return null;
    const meta = (species.isolates || [])[index];
    if (!meta) return null;
    return {
      name: (meta.names || [])[0] || meta.designation || '',
      rank: 'isolate', n_species: 0, tiers: {}, top_tier: null,
      note: null, meta,
    };
  }

  /* Fields the server always sends for a node of this rank, with the value
     it sends when there is no record. The export drops an empty field, so it
     is put back here: the application distinguishes "nothing known" from
     "this rank has no such thing", and so does anything reading the JSON.
     crossreact is a list of complexes, so its empty value is a list. */
  const EMPTY = {
    species: { morphology: null, baltimore: null, receptors: null,
               biosafety: null, countermeasures: null, therapeutics: null,
               crossreact: [] },
    genus: { morphology: null, crossreact: [] },
    serogroup: { morphology: null, crossreact: [] },
    isolate: {},
    group: { morphology: null },      // every other rank above species
  };

  /** Put back what export_static.py hoisted into tables.json.
   *
   * The reference fields are removed again afterwards: they are this file's
   * bookkeeping, and leaving them on the record would be the one place the
   * hosted copy's data differed in shape from the server's. */
  function rehydrate(id, rec) {
    if (!rec) return null;
    const out = { ...rec, id };
    if (rec.morphology_key) out.morphology = tables.morphology[rec.morphology_key];
    if (rec.baltimore_key) {
      out.baltimore = { ...tables.baltimore[rec.baltimore_key],
                        note: rec.baltimore_note ?? null };
    }
    for (const f of ['biosafety', 'receptors', 'countermeasures',
                     'therapeutics', 'crossreact']) {
      const ref = rec[`${f}_ref`];
      if (ref && tables[f][ref]) out[f] = tables[f][ref];
    }
    for (const k of ['morphology_key', 'baltimore_key', 'baltimore_note',
                     'biosafety_ref', 'receptors_ref', 'countermeasures_ref',
                     'therapeutics_ref', 'crossreact_ref']) {
      delete out[k];
    }
    for (const [f, empty] of Object.entries(EMPTY[rec.rank] || EMPTY.group)) {
      if (out[f] === undefined) out[f] = Array.isArray(empty) ? [] : empty;
    }
    return out;
  }

  /* ------------------------------------------------------- tier overrides */

  const readOverrides = () => {
    try { return JSON.parse(localStorage.getItem(OVERRIDES_KEY) || '{}'); }
    catch { return {}; }
  };
  const writeOverrides = o => {
    try { localStorage.setItem(OVERRIDES_KEY, JSON.stringify(o)); }
    catch { /* private browsing; the correction is lost, which the UI says */ }
  };

  /** Apply a stored correction to a node record, as the server would. */
  function applyOverride(rec) {
    if (!rec || rec.rank !== 'species') return rec;
    const ov = readOverrides()[rec.name];
    if (!ov) return rec;
    const meta = { ...(rec.meta || {}) };
    meta.base_tier = meta.base_tier ?? meta.tier;
    meta.base_basis = meta.base_basis ?? meta.basis;
    meta.tier = ov.tier;
    meta.basis = 'override';
    meta.override = ov;
    return { ...rec, meta, tier: ov.tier };
  }

  /* ------------------------------------------------------------- handlers */

  const H = {};

  H['meta'] = async () => {
    const m = await load('meta.json');
    return json({ ...m, static: true });
  };

  /** A node as the tree draws it: the server's shallow(), reproduced.
   *
   * The counts matter more than they look. app.js calls a row a leaf when
   * n_children is 0, so a row without the field is never a leaf and every
   * isolate sprouts a disclosure arrow that opens on nothing. */
  function row(id, rec, parentMeta) {
    const r = applyOverride(rec);
    const meta = r.meta || {};
    const isolates = r.isolates || [];
    const out = {
      id, name: r.name, rank: r.rank,
      n_children: r.rank === 'species'
        ? isolates.length : (r.children || []).length,
      n_species: r.n_species ?? 0,
      top_tier: r.top_tier ?? null,
      tiers: r.tiers || {},
    };
    if (r.rank === 'species') {
      out.tier = meta.tier ?? null;
      out.basis = meta.basis ?? null;
      out.profiled = !!meta.profiled;
      out.serogroup = meta.serogroup ?? null;
      out.genome = meta.genome ?? null;
      out.n_isolates = isolates.length;
      const names = isolates.flatMap(m => (m && m.names) || []);
      out.common = names.length ? names[0] : null;
    } else if (r.rank === 'isolate') {
      out.meta = meta;
      // An isolate has no tier of its own; it shows its species'.
      out.tier = (parentMeta || {}).tier ?? null;
      out.common = (meta.abbrev || []).join('; ') || meta.designation || null;
    }
    return out;
  }

  /** sort_children: by name, with the Unassigned buckets last. */
  const byName = (a, b) => {
    const au = /^Unassigned/.test(a.name) ? 1 : 0;
    const bu = /^Unassigned/.test(b.name) ? 1 : 0;
    if (au !== bu) return au - bu;
    const x = a.name.toLowerCase(), y = b.name.toLowerCase();
    return x < y ? -1 : x > y ? 1 : 0;
  };

  /** The rows beneath a node. A species' are its isolates. */
  async function childRows(id, raw) {
    if (raw.rank === 'isolate') return [];
    if (raw.rank === 'species') {
      // Isolate ids follow the record's own order; the listing is sorted,
      // as the server sorts it.
      const meta = (applyOverride(raw) || {}).meta || {};
      return (raw.isolates || [])
        .map((m, i) => row(`${id}/i${i}`, isolateRecord(raw, i), meta))
        .filter(Boolean)
        .sort(byName);
    }
    const out = [];
    for (const c of (raw.children || [])) {
      const cid = typeof c === 'string' ? c : c && c.id;
      if (!cid) continue;
      const rec = await nodeRaw(cid);
      if (rec) out.push(row(cid, rec));
    }
    return out;
  }

  H['children'] = async p => {
    await boot();
    const id = p.get('id') || 'root';
    const raw = await nodeRaw(id);
    if (!raw) return json({ error: 'not found' }, 404);
    return json({ id, children: await childRows(id, raw) });
  };

  H['node'] = async p => {
    await boot();
    const id = p.get('id') || '';
    const raw = await nodeRaw(id);
    if (!raw) return json({ error: 'not found' }, 404);
    const rec = applyOverride(rehydrate(id, raw));
    rec.path = await ancestry(id);
    if (rec.rank === 'species') {
      delete rec.children;
    } else if (rec.rank === 'isolate') {
      // Clinical information lives on the species, and the server sends the
      // species' record along so the isolate view has something to show.
      const spId = id.split('/').slice(0, -1).join('/');
      const sp = rehydrate(spId, await nodeRaw(spId));
      if (sp) {
        rec.species = {
          id: spId, name: sp.name,
          meta: (applyOverride(sp) || {}).meta ?? null,
          isolates: sp.isolates || [],
        };
        rec.morphology = sp.morphology ?? null;
        rec.geo = sp.geo ?? null;
      }
    } else {
      // groupDetail renders d.children itself, so these have to be rows.
      rec.children = await childRows(id, raw);
    }
    return json(rec);
  };

  /* The radial view's bounded subtree, reproducing api_subtree: breadth by
     species count, budget shared out by sqrt(species) so the biggest branch
     cannot swallow it, and the top level never trimmed. */
  H['subtree'] = async p => {
    await boot();
    const rootId = p.get('id') || 'root';
    const depth = Math.max(1, Math.min(+(p.get('depth') || 3), 6));
    const fan = Math.max(4, Math.min(+(p.get('fan') || 36), 200));
    const budget = 600;
    const out = {};
    let count = 0;

    async function visit(id, level, limit) {
      const raw = skeleton[id] || await nodeRaw(id);
      if (!raw) return 0;
      const ov = applyOverride(rehydrate(id, raw));
      const meta = ov.meta || {};
      const rec = {
        id, name: raw.name, rank: raw.rank,
        n_species: raw.n_species ?? 0,
        tier: raw.rank === 'species' ? (meta.tier ?? raw.tier) : raw.top_tier,
        basis: meta.basis ?? null,
        profiled: !!meta.profiled,
        serogroup: meta.serogroup ?? null,
        children: [], truncated: 0, has_more: false,
      };
      out[id] = rec;
      count += 1;
      let used = 1;

      const kidIds = [];
      for (const c of (raw.children || [])) {
        const cid = typeof c === 'string' ? c : c && c.id;
        if (!cid) continue;
        const k = skeleton[cid] || await nodeRaw(cid);
        if (k && k.rank !== 'isolate') kidIds.push([cid, k]);
      }
      if (!kidIds.length) return used;
      if (level >= depth || count >= budget || used >= limit) {
        rec.has_more = true;
        return used;
      }
      kidIds.sort((a, b) => (b[1].n_species || 0) - (a[1].n_species || 0) ||
                            a[1].name.localeCompare(b[1].name));
      const width = raw.rank === 'root' ? kidIds.length : fan;
      const shown = kidIds.slice(0, width);
      const hidden = kidIds.length - shown.length;
      const weights = shown.map(([, k]) => Math.max(1, Math.sqrt(k.n_species || 1)));
      for (let i = 0; i < shown.length; i++) {
        if (count >= budget || used >= limit) { rec.truncated += 1; continue; }
        const rest = weights.slice(i).reduce((a, b) => a + b, 0) || 1;
        const share = Math.max(2, Math.floor((limit - used) * weights[i] / rest));
        rec.children.push(shown[i][0]);
        used += await visit(shown[i][0], level + 1, share);
      }
      if (hidden > 0) rec.truncated += hidden;
      return used;
    }

    await visit(rootId, 0, budget);
    return json({
      root: rootId, depth, fan, nodes: out,
      path: await ancestry(rootId), total_nodes: Object.keys(out).length,
    });
  };

  /* search.json is 7 MB, so it loads on the first search rather than at
     boot. The ranking is the server's, term for term. */
  const RANK_WEIGHT = {
    species: 0, clade: 1, serogroup: 2, subgenus: 3, genus: 4, subfamily: 5,
    family: 6, order: 7, suborder: 7, class: 8, subclass: 8, phylum: 9,
    subphylum: 9, kingdom: 10, subkingdom: 10, subrealm: 11, realm: 11, root: 12,
  };

  H['search'] = async p => {
    const q = (p.get('q') || '').trim();
    if (q.length < 2) return json({ q, results: [] });
    await boot();
    const index = await load('search.json');
    const needle = fold(q);
    const tierFilter = p.get('tier') || null;
    const exact = new RegExp(`(^|\\|\\s|\\s)${esc(needle)}($|\\s|\\|)`);
    const starts = new RegExp(`(^|\\|\\s|\\s)${esc(needle)}`);

    const scored = [];
    for (const e of index) {
      const hay = fold(e.terms.join(' | '));
      if (!hay.includes(needle)) continue;
      if (tierFilter && e.tier !== tierFilter) continue;
      const score = exact.test(hay) ? 0
        : hay.startsWith(needle) ? 1
        : starts.test(hay) ? 2 : 3;
      scored.push([score, RANK_WEIGHT[e.rank] ?? 12,
                   e.profiled ? 0 : 1, e.name.length, e]);
    }
    scored.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2] || a[3] - b[3]);

    const results = [];
    for (const row of scored.slice(0, 60)) {
      const e = row[4];
      results.push({
        id: e.id, name: e.name, rank: e.rank, tier: e.tier,
        serogroup: e.serogroup, family: e.family, profiled: e.profiled,
        n_species: e.n_species,
        matched: e.terms.filter(t => fold(t).includes(needle)).slice(0, 4),
        path: (await ancestry(e.id)).slice(1, -1).map(a => a.name),
      });
    }
    return json({ q, total: scored.length, results });
  };

  H['pathogens'] = async () => json(await load('pathogens.json'));

  /* ------------------------------------------------------------- travel */

  const countrySlug = n => n.toLowerCase().replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  function windowVerdict(win, days) {
    if (days == null) return 'unfiltered';
    if (!win) return 'unknown';
    if (days < win[0]) return 'early';
    if (days > win[1]) return 'late';
    return 'plausible';
  }

  H['travel'] = async p => {
    const country = (p.get('country') || '').trim();
    const index = await load('travel-index.json');
    if (!country) return json(index);

    const match = index.countries.find(c =>
      c.toLowerCase() === country.toLowerCase());
    if (!match) {
      const low = country.toLowerCase();
      return json({
        country, known_country: false, asked: country,
        suggestions: index.countries.filter(c => c.toLowerCase().includes(low)).slice(0, 8),
        regional: [], groups: [], worldwide: [], counts: {},
      });
    }

    const daysRaw = p.get('days');
    const days = daysRaw === null || daysRaw === '' ? null
      : Math.max(0, Math.min(parseInt(daysRaw, 10) || 0, 3650));
    const route = p.get('route') || null;

    const [base, worldwide] = await Promise.all([
      load(`travel/${countrySlug(match)}.json`), load('travel-worldwide.json'),
    ]);
    const stamp = e => ({ ...e, window: windowVerdict(e.incubation_days, days) });
    let regional = (base.regional || []).map(stamp);
    let cosmo = worldwide.map(stamp);
    if (route) {
      regional = regional.filter(r => (r.routes || []).includes(route));
      cosmo = cosmo.filter(r => (r.routes || []).includes(route));
    }

    const ATTR = new Set(['vertical']);
    const order = index.routes.map(r => r.key);
    const groups = [];
    for (const key of order) {
      if (ATTR.has(key)) continue;
      const members = regional.filter(r => (r.routes || []).includes(key));
      if (members.length) {
        groups.push({
          route: key,
          label: (index.routes.find(r => r.key === key) || {}).label || 'Unclear',
          entries: members,
        });
      }
    }
    // What WHO and UKHSA are currently reporting from there, as the server
    // attaches it: items whose title names the country and that matched a
    // pathogen. A source that cannot be reached leaves the block out rather
    // than failing the lookup.
    let signals = [], sources = [];
    try {
      const live = await allSignals();
      const low = match.toLowerCase();
      sources = live.sources;
      signals = live.signals
        .filter(r => r.taxon && (r.title || '').toLowerCase().includes(low))
        .slice(0, 12);
    } catch { /* the exposure list is the answer; reporting is a bonus */ }

    const n = v => regional.filter(r => r.window === v).length;
    return json({
      ...base, asked: country, known_country: true,
      signals, signal_sources: sources,
      days_since_return: days, route,
      regional, groups, worldwide: cosmo,
      counts: {
        regional: regional.length, worldwide: cosmo.length,
        plausible: n('plausible'), late: n('late'), early: n('early'),
        unknown_window: n('unknown'),
        human_evidence: regional.filter(r => r.evidence === 'human').length,
        reservoir_only: regional.filter(r =>
          ['reservoir', 'vector', 'human-serology'].includes(r.evidence)).length,
      },
    });
  };

  H['differential'] = async p => {
    const syndrome = p.get('syndrome') || '';
    const index = await load('differential-index.json');
    if (!syndrome) return json(index);

    const file = await load(`differential/${syndrome}.json`);
    const country = (p.get('country') || '').trim();
    const route = p.get('route') || null;
    const daysRaw = p.get('days');
    const days = daysRaw === null || daysRaw === '' ? null
      : Math.max(0, Math.min(parseInt(daysRaw, 10) || 0, 3650));

    let rows = file.candidates.map(c => ({ ...c }));
    let resolved = null;
    if (country) {
      const t = await (await H['travel'](
        new URLSearchParams({ country, ...(daysRaw ? { days: daysRaw } : {}) }))).json();
      if (t.known_country) {
        resolved = t.country;
        const facts = new Map();
        for (const r of [...t.regional, ...t.worldwide]) facts.set(r.species, r);
        rows = rows.filter(r => facts.has(r.species)).map(r => {
          const f = facts.get(r.species);
          return {
            ...r, routes: f.routes, evidence: f.evidence,
            evidence_label: f.evidence_label, geo_inferred: f.geo_inferred,
            geo_region: f.geo_region, incubation: f.incubation,
            incubation_days: f.incubation_days, window: f.window,
            scope: f.scope,
          };
        });
      } else {
        rows = [];
      }
    }
    if (route) rows = rows.filter(r => (r.routes || []).includes(route));
    if (days != null) {
      rows = rows.filter(r => r.window == null ||
        ['plausible', 'unknown', 'unfiltered'].includes(r.window));
    }
    return json({
      syndrome, label: file.label, note: file.note,
      country: resolved, asked_country: country || null,
      known_country: country ? !!resolved : null,
      route, days_since_return: days,
      candidates: rows.slice(0, 60),
      counts: { total: Math.min(rows.length, 60),
                unfiltered: file.candidates.length },
    });
  };

  /* --------------------------------------------- live, cross-origin sources */

  /* Europe PMC. Reproduces atlas/enrich.py: relevance order, and the human
     flag requires the virus name and a human term in the SAME sentence,
     because "human" anywhere in an abstract flagged an archaeal virus. */
  H['evidence'] = async p => {
    await boot();
    const id = p.get('id') || '';
    let rec = await nodeRaw(id);
    let nodeId = id;
    if (rec && rec.rank === 'isolate') {
      nodeId = id.split('/').slice(0, -1).join('/');
      rec = await nodeRaw(nodeId);
    }
    if (!rec) return json({ error: 'not found' }, 404);
    const full = rehydrate(nodeId, rec);
    const names = new Set([full.name]);
    for (const iso of (full.isolates || [])) {
      for (const nm of (iso.names || [])) names.add(nm);
    }
    const terms = [...names].slice(0, 6);
    const query = terms.map(t => `"${t.replace(/"/g, '')}"`).join(' OR ');
    const url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='
      + encodeURIComponent(query)
      + '&format=json&pageSize=40&resultType=core';
    let papers = [];
    try {
      const res = await fetch(url);
      const data = await res.json();
      const rx = new RegExp(terms.map(t => esc(t)).join('|'), 'i');
      const human = /\bhuman|\bpatient|\bclinical|\bchild|\binfant|\bperson/i;
      papers = ((data.resultList || {}).result || []).map(h => {
        const title = h.title || '';
        const abstract = (h.abstractText || '').replace(/<[^>]+>/g, ' ');
        const band = rx.test(title) ? 'title'
          : rx.test(abstract) ? 'abstract' : 'weak';
        const sentences = (title + '. ' + abstract).split(/(?<=[.!?])\s+/);
        return {
          title, abstract: abstract.slice(0, 1200),
          journal: h.journalTitle || h.bookOrReportDetails?.publisher || '',
          year: h.pubYear, pmid: h.pmid, doi: h.doi,
          cited: h.citedByCount || 0,
          open: h.isOpenAccess === 'Y',
          band,
          human: sentences.some(s => rx.test(s) && human.test(s)),
        };
      });
      const order = { title: 0, abstract: 1, weak: 2 };
      papers.sort((a, b) => order[a.band] - order[b.band] || b.cited - a.cited);
    } catch (err) {
      return json({ id: nodeId, species: full.name, literature: [],
                    error: `Europe PMC unreachable: ${err.message}` });
    }
    return json({
      id: nodeId, species: full.name, terms,
      literature: papers, fetched_at: Date.now() / 1000, source: 'Europe PMC',
    });
  };

  /* WHO Disease Outbreak News and UKHSA, fetched straight from the source
     and classified against diseases.json. Memoised for the life of the page,
     the way the server caches them, so the travel panel and the signals
     panel do not each go and ask. */
  let signalsOnce = null;
  const allSignals = () => (signalsOnce = signalsOnce || signalsFetch());

  /* surveil._strip: tags out, the handful of entities WHO and gov.uk emit
     decoded, whitespace collapsed. Without it a summary kept its \r\n and
     &nbsp; and no longer matched what the server sends. */
  const strip = h => (h || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&#39;/g, "'").replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ').trim();

  async function signalsFetch() {
    const spec = await load('diseases.json');
    const compiled = spec.diseases.map(d => ({ ...d, re: new RegExp(d.rx, 'i') }));
    const nonViral = new RegExp(spec.non_viral, 'i');
    const reports = [];
    const sources = [];

    try {
      const who = await (await fetch(
        'https://www.who.int/api/news/diseaseoutbreaknews'
        + '?$orderby=PublicationDateAndTime%20desc&$top=100'
        + '&$select=Title,PublicationDateAndTime,UrlName,Summary')).json();
      for (const r of (who.value || [])) {
        reports.push({
          source: 'WHO', title: (r.Title || '').trim(),
          date: (r.PublicationDateAndTime || '').slice(0, 10),
          summary: strip(r.Summary).slice(0, 600),
          url: `https://www.who.int/emergencies/disease-outbreak-news/item/${r.UrlName}`,
        });
      }
      sources.push({ source: 'WHO', state: 'fetched', error: null,
                     fetched_at: Date.now() / 1000 });
    } catch (e) {
      sources.push({ source: 'WHO', state: 'failed', error: e.message });
    }

    try {
      const uk = await (await fetch(
        'https://www.gov.uk/api/search.json'
        + '?filter_organisations=uk-health-security-agency'
        + '&count=100&order=-public_timestamp'
        + '&fields=title,link,public_timestamp,description')).json();
      const keep = /outbreak|surveillance|incident|cluster|cases? of|epidemiolog|risk assessment|health protection report|rapid risk|situation (report|update)|detected/i;
      const drop = /leaflet|consultation|vacanc|job description|annual report|terms of reference|minutes of|guidance for parents|patient information|\bform\b|freedom of information|all-cause mortality|syndromic surveillance|ambulance|out-of-hours|emergency department|NHS 111/i;
      const seen = new Set();
      for (const r of (uk.results || [])) {
        const title = (r.title || '').trim();
        if (!keep.test(title) || drop.test(title)) continue;
        const stem = title.replace(/[,:]?\s*(week|wk)\s*\d+.*$/i, '')
          .replace(/\b(19|20)\d{2}(\s*(to|-|\/)\s*(19|20)?\d{2})?\b/g, '')
          .replace(/\s+/g, ' ').trim().toLowerCase();
        if (seen.has(stem)) continue;
        seen.add(stem);
        reports.push({
          source: 'UKHSA', title,
          date: (r.public_timestamp || '').slice(0, 10),
          summary: strip(r.description).slice(0, 600),
          url: r.link && r.link.startsWith('http') ? r.link
            : 'https://www.gov.uk' + (r.link || ''),
        });
      }
      sources.push({ source: 'UKHSA', state: 'fetched', error: null,
                     fetched_at: Date.now() / 1000 });
    } catch (e) {
      sources.push({ source: 'UKHSA', state: 'failed', error: e.message });
    }

    reports.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    const signals = reports.map(r => {
      const hit = compiled.find(d => d.re.test(r.title))
        || compiled.find(d => d.re.test(r.summary || ''));
      if (hit) {
        return { ...r, kind: hit.kind, taxon: hit.taxon,
                 disease: hit.label, node: hit.node };
      }
      return { ...r, kind: nonViral.test(r.title) ? 'non-viral' : 'unmatched' };
    });
    return {
      signals, sources,
      // The server also probes for the week's ECDC threat report. That one
      // cannot be done here: ecdc.europa.eu sends no access-control-allow-
      // origin, so the browser is not allowed to read even the HEAD. The
      // panel leaves the block out rather than inventing a link.
      ecdc: null,
      counts: {
        total: signals.length,
        matched: signals.filter(s => s.taxon).length,
        non_viral: signals.filter(s => s.kind === 'non-viral').length,
        unmatched: signals.filter(s => s.kind === 'unmatched').length,
      },
    };
  }

  H['signals'] = async () => json(await allSignals());

  H['genomic'] = async p => {
    await boot();
    const id = p.get('id') || '';
    let rec = await nodeRaw(id);
    let nodeId = id;
    if (rec && rec.rank === 'isolate') {
      nodeId = id.split('/').slice(0, -1).join('/');
      rec = await nodeRaw(nodeId);
    }
    if (!rec) return json({ error: 'not found' }, 404);
    const all = await load('genomic.json');
    const builds = all[rec.name] || [];
    if (!builds.length || p.get('summary') !== '1') {
      return json({ species: rec.name, builds, summaries: [] });
    }
    // Each dataset is several megabytes, so they are fetched in parallel and
    // reduced to the same summary the server produced.
    const summaries = await Promise.all(builds.map(async b => {
      try {
        const res = await fetch(
          'https://nextstrain.org/charon/getDataset?prefix=/' + b.prefix,
          { headers: { accept: 'application/vnd.nextstrain.dataset.main+json' } });
        const data = await res.json();
        const acc = { tips: 0, country: {}, clade: {} };
        (function walk(n) {
          const kids = n.children || [];
          if (!kids.length) {
            acc.tips += 1;
            const a = n.node_attrs || {};
            const c = (a.country || {}).value;
            if (c) acc.country[c] = (acc.country[c] || 0) + 1;
            const cl = (a.clade_membership || a.clade || a.lineage || {}).value;
            if (cl) acc.clade[cl] = (acc.clade[cl] || 0) + 1;
          }
          kids.forEach(walk);
        })(Array.isArray(data.tree) ? { children: data.tree } : data.tree || {});
        const top = (o, n) => Object.entries(o).sort((x, y) => y[1] - x[1])
          .slice(0, n).map(([name, k]) => ({ name, n: k }));
        const meta = data.meta || {};
        return {
          prefix: b.prefix, url: b.url, title: meta.title || b.label,
          updated: meta.updated, genomes: acc.tips,
          clades: top(acc.clade, 6), countries: top(acc.country, 12),
          regions: [], state: 'fetched', error: null,
        };
      } catch (err) {
        return { prefix: b.prefix, url: b.url, title: b.label,
                 state: 'failed', error: err.message, genomes: 0,
                 clades: [], countries: [] };
      }
    }));
    return json({ species: rec.name, builds, summaries });
  };

  /* -------------------------------------------- corrections in localStorage */

  async function recomputeChain(speciesId) {
    // The server rolled tier counts up the ancestry. Here the client only
    // needs the ids so the tree can repaint; the tiers themselves are
    // recomputed from the overrides on next read.
    const chain = await ancestry(speciesId);
    const out = [];
    for (const a of chain.reverse()) {
      const rec = skeleton[a.id] || await nodeRaw(a.id);
      out.push({ id: a.id, top_tier: rec ? rec.top_tier : null,
                 tiers: rec ? rec.tiers || {} : {} });
    }
    return out;
  }

  H['tier:POST'] = async (p, body) => {
    await boot();
    const id = body.id || '';
    let rec = await nodeRaw(id);
    let nodeId = id;
    if (rec && rec.rank === 'isolate') {
      nodeId = id.split('/').slice(0, -1).join('/');
      rec = await nodeRaw(nodeId);
    }
    if (!rec) return json({ error: 'unknown node' }, 404);
    if (rec.rank !== 'species') {
      return json({ error: 'tiers are held on species' }, 400);
    }
    const meta = rec.meta || {};
    const entry = {
      tier: body.tier, note: (body.note || '').trim(), by: 'browser',
      at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
      was: meta.base_tier ?? meta.tier,
    };
    const all = readOverrides();
    all[rec.name] = entry;
    writeOverrides(all);
    return json({
      id: nodeId, species: rec.name, tier: body.tier, basis: 'override',
      override: entry, tiers: { [body.tier]: 1 },
      path_tiers: await recomputeChain(nodeId),
      count: Object.keys(all).length, stored: 'localStorage',
    });
  };

  H['tier:DELETE'] = async p => {
    await boot();
    const id = p.get('id') || '';
    const rec = await nodeRaw(id);
    if (!rec) return json({ error: 'unknown node' }, 404);
    const all = readOverrides();
    const had = rec.name in all;
    delete all[rec.name];
    writeOverrides(all);
    const meta = rec.meta || {};
    return json({
      id, species: rec.name, cleared: had,
      tier: meta.base_tier ?? meta.tier, basis: meta.base_basis ?? meta.basis,
      tiers: rec.tiers || {}, path_tiers: await recomputeChain(id),
      count: Object.keys(all).length,
    });
  };

  H['corrections'] = async () => {
    const all = readOverrides();
    const meta = await load('meta.json');
    const rows = Object.entries(all).map(([species, e]) => ({
      species, id: null, matched: true, tier: e.tier, was: e.was,
      note: e.note, at: e.at,
    })).sort((a, b) => (b.at || '').localeCompare(a.at || ''));
    return json({ corrections: rows, legend: meta.tiers });
  };

  /* ------------------------------------------------------------ intercept */

  const nativeFetch = window.fetch.bind(window);

  window.fetch = async function (input, init) {
    const url = typeof input === 'string' ? input
      : input instanceof URL ? input.href : (input && input.url) || '';
    const m = /(?:^|\/)api\/([a-z]+)(?:\?|$)/.exec(
      url.startsWith('http') ? new URL(url).pathname + new URL(url).search : url);
    if (!m) return nativeFetch(input, init);

    const name = m[1];
    const method = ((init && init.method) || 'GET').toUpperCase();
    const params = new URLSearchParams(
      (url.split('?')[1] || '').replace(/^\?/, ''));
    const handler = H[`${name}:${method}`] || H[name];
    if (!handler) return nativeFetch(input, init);

    try {
      let body = {};
      if (init && init.body) { try { body = JSON.parse(init.body); } catch {} }
      return await handler(params, body);
    } catch (err) {
      console.error(`static api: ${name} failed`, err);
      return json({ error: String(err && err.message || err) }, 500);
    }
  };

  window.__STATIC_ATLAS__ = { load, readOverrides, cache };
})();
