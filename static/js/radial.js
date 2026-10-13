/*! Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
 *  Proprietary. No licence granted; see LICENSE. */
/* Virus Atlas — radial taxonomy tree (D3).
 *
 * A circular cladogram of the ICTV hierarchy. Leaves sit on the outer ring,
 * each rank on its own ring, links drawn as smooth radial Béziers.
 *
 * This is a TAXONOMY, not an inferred phylogeny — ICTV ranks, not sequence
 * distance — so radius encodes rank depth only and the view says so. Calling
 * it a phylogram would imply branch lengths that do not exist here.
 *
 * Viruses are POLYPHYLETIC. ICTV realms are each defined by a signature gene
 * set (RdRp, HK97 fold, jelly-roll capsid…) with no demonstrated homology
 * between them, and a long tail of taxa sits outside every realm. "All
 * viruses" is therefore a container, not an ancestor. At that level the view
 * switches to SPLIT mode: each independent lineage gets its own wedge with a
 * visible gap, nothing is linked across the centre, and the centre stays
 * empty. Drawing a single root there would assert a common ancestor that
 * the data does not support.
 *
 * Re-rooting animates: nodes interpolate along their arcs from where they were
 * to where they belong, entering from their parent's old position so the eye
 * can follow the change rather than being cut to a new picture.
 */

const Radial = (() => {

  const TAU = Math.PI * 2;
  const DUR = 680;                       // master transition duration (ms)
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const dur = () => (reduceMotion ? 0 : DUR);

  let el, svg, gRoot, gRings, gLinks, gNodes, gLabels, gArcs, tip, zoomBehaviour;
  let data = null, rootId = null, onSelect = null;
  let depth = 3, fan = 36, radius = 404;
  let prevPos = new Map();               // node id -> {x, y} from the last render
  let busy = false;

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* ------------------------------------------------------------ helpers */

  // "Orthobunyavirus catqueense" -> "O. catqueense"; the genus is the ring above.
  const shortSpecies = name => {
    const p = name.split(' ');
    return p.length > 1 ? `${p[0][0]}. ${p.slice(1).join(' ')}` : name;
  };

  const labelOf = d => {
    const n = d.data;
    const base = n.rank === 'species' ? shortSpecies(n.name) : n.name;
    return n.truncated ? `${base} +${n.truncated}` : base;
  };

  const nodeRadius = d => d.data.rank === 'species'
    ? 3.6
    : Math.min(10, 4 + Math.log10((d.data.n_species || 1) + 1) * 2.3);

  /** Build a d3.hierarchy from the flat {id: node} payload. */
  function toHierarchy(payload) {
    const { nodes, root } = payload;
    const build = id => {
      const n = nodes[id];
      return { ...n, kids: (n.children || []).filter(c => nodes[c]).map(build) };
    };
    return d3.hierarchy(build(root), d => d.kids);
  }

  /** Point on a circle, in the same convention d3's radial layouts use. */
  const polar = (r, a) => [Math.sin(a) * r, -Math.cos(a) * r];

  /** An arc as a path, run backwards through the lower half so text stays upright. */
  function arcPath(r, a0, a1) {
    const flip = flipped((a0 + a1) / 2);
    const [s, e] = flip ? [a1, a0] : [a0, a1];
    const [x0, y0] = polar(r, s), [x1, y1] = polar(r, e);
    const big = Math.abs(a1 - a0) > Math.PI ? 1 : 0;
    return `M${x0.toFixed(2)},${y0.toFixed(2)}` +
           `A${r},${r} 0 ${big} ${flip ? 0 : 1} ${x1.toFixed(2)},${y1.toFixed(2)}`;
  }

  /**
   * Give every top-level lineage its own wedge, separated by a real gap.
   *
   * Each wedge is sized by how many tips the lineage contributes, then the
   * subtree's own angular extent is rescaled into it. The gaps are the whole
   * point: they are what says "these are not joined up", so they are taken
   * out of the circle before the wedges are shared out, never squeezed in
   * afterwards.
   */
  function wedges(root) {
    const kids = root.children || [];
    if (!kids.length) return [];
    // Width by diversity, not by how many nodes happen to be drawn: a realm
    // cut off at phylum level shows few tips but holds thousands of species.
    // sqrt keeps Riboviria dominant without reducing the rest to slivers, and
    // the leaf count is a floor so a wedge is never narrower than it can draw.
    const weight = k => Math.max(k.leaves().length, Math.sqrt(k.data.n_species || 1));
    const total = d3.sum(kids, weight) || 1;
    const gap = Math.min(0.05, (TAU * 0.16) / kids.length);
    const avail = TAU - gap * kids.length;
    let cur = gap / 2;
    return kids.map(k => {
      const span = (avail * weight(k)) / total;
      const ds = k.descendants();
      const lo = d3.min(ds, d => d.x), hi = d3.max(ds, d => d.x);
      const k2 = hi > lo ? span / (hi - lo) : 0;
      ds.forEach(d => { d.x = hi > lo ? cur + (d.x - lo) * k2 : cur + span / 2; });
      const w = { node: k, a0: cur, a1: cur + span, mid: cur + span / 2, span };
      cur += span + gap;
      return w;
    });
  }

  /* ------------------------------------------------------------- render */

  function render({ animate = true } = {}) {
    if (!data) return;
    const root = toHierarchy(data);

    // d3.cluster puts every leaf on the outer ring — the dendrogram look that
    // suits a taxonomy, where all tips are equally "current".
    d3.cluster().size([TAU, radius]).separation((a, b) =>
      (a.parent === b.parent ? 1 : 1.8) / Math.max(1, a.depth))(root);

    const maxDepth = d3.max(root.descendants(), d => d.depth) || 1;

    // "All viruses" is a container with no ancestor behind it, so at that level
    // the lineages are laid out as separate wedges and the hub is left empty.
    const split = data.nodes[data.root]?.rank === 'root';
    const inner = split ? radius * 0.2 : 0;
    const ringR = i => split
      ? inner + ((i - 1) / Math.max(1, maxDepth - 1)) * (radius - inner)
      : (i / maxDepth) * radius;

    // Even rings by rank depth rather than by cluster's own spacing.
    root.each(d => { d.y = d.depth === 0 ? 0 : ringR(d.depth); });
    const lineages = split ? wedges(root) : [];
    el.classList.toggle('is-split', split);
    svg.classed('is-split', split);

    const t = d3.transition().duration(animate ? dur() : 0).ease(d3.easeCubicInOut);

    /* rings + rank labels ------------------------------------------------ */
    // A ring can hold more than one rank -- some serogroups have an antigenic
    // clade below them, others go straight to species. Label the ring with the
    // rank that dominates it, marked "+" when it is mixed, rather than with
    // whichever node happened to be visited first.
    const ranksAt = {};
    root.each(d => {
      if (!d.depth) return;
      (ranksAt[d.depth] = ranksAt[d.depth] || []).push(d.data.rank);
    });
    const ringData = d3.range(1, maxDepth + 1).map(i => {
      const list = ranksAt[i] || [];
      const tally = d3.rollup(list, v => v.length, r => r);
      const top = [...tally.entries()].sort((a, b) => b[1] - a[1])[0];
      return {
        d: i,
        r: ringR(i),
        rank: top ? top[0] + (tally.size > 1 ? ' +' : '') : '',
      };
    });

    gRings.selectAll('circle.rad-ring')
      .data(ringData, d => d.d)
      .join(
        e => e.append('circle').attr('class', 'rad-ring').attr('r', 0),
        u => u, x => x.transition(t).attr('r', 0).remove())
      .transition(t).attr('r', d => d.r);

    gRings.selectAll('text.rad-ring-lab')
      .data(ringData, d => d.d)
      .join(
        e => e.append('text').attr('class', 'rad-ring-lab').attr('opacity', 0),
        u => u, x => x.transition(t).attr('opacity', 0).remove())
      .text(d => d.rank)
      .transition(t).attr('opacity', 1).attr('x', 5).attr('y', d => -d.r - 4);

    /* links --------------------------------------------------------------- */
    const link = d3.linkRadial().angle(d => d.x).radius(d => d.y);
    const linkKey = d => `${d.source.data.id}>${d.target.data.id}`;

    // In split mode the root's own links are dropped: nothing crosses the hub.
    const links = root.links().filter(l => !split || l.source.depth > 0);

    gLinks.selectAll('path')
      .data(links, linkKey)
      .join(
        enter => enter.append('path')
          .attr('class', 'rad-link')
          .attr('data-id', d => d.target.data.id)
          .attr('data-tier', d => d.target.data.tier || 'no-evidence')
          .attr('d', d => {
            const from = prevPos.get(d.source.data.id) || { x: d.source.x, y: 0 };
            return link({ source: from, target: from });
          })
          .attr('opacity', 0),
        update => update,
        exit => exit.transition(t).attr('opacity', 0).remove())
        .attr('data-tier', d => d.target.data.tier || 'no-evidence')
        .transition(t)
        .attr('opacity', 1)
        .attrTween('d', function (d) {
          const from = prevPos.get(d.target.data.id)
            || prevPos.get(d.source.data.id)
            || { x: d.source.x, y: 0 };
          const s0 = prevPos.get(d.source.data.id) || { x: d.source.x, y: 0 };
          const si = d3.interpolate(s0, { x: d.source.x, y: d.source.y });
          const ti = d3.interpolate(from, { x: d.target.x, y: d.target.y });
          return u => link({ source: si(u), target: ti(u) });
        });

    /* nodes ---------------------------------------------------------------- */
    const shown = root.descendants().filter(d => !split || d.depth > 0);

    const nodeSel = gNodes.selectAll('g.rad-node')
      .data(shown, d => d.data.id)
      .join(
        enter => {
          const g = enter.append('g')
            .attr('class', d => `rad-node${d.data.profiled ? ' profiled' : ''}`)
            .attr('data-id', d => d.data.id)
            .attr('data-rank', d => d.data.rank)
            .attr('transform', d => {
              const p = prevPos.get(d.parent?.data.id) || { x: d.x, y: 0 };
              return `rotate(${p.x * 180 / Math.PI - 90}) translate(${p.y},0)`;
            })
            .attr('opacity', 0);
          g.append('circle')
            .attr('class', 'rad-dot')
            .attr('data-id', d => d.data.id)
            .attr('r', 0);
          g.append('path').attr('class', 'rad-stub');
          g.append('title');
          return g;
        },
        update => update,
        exit => exit.transition(t).attr('opacity', 0)
          .attr('transform', d => `rotate(${d.x * 180 / Math.PI - 90}) translate(0,0)`)
          .remove());

    nodeSel
      .attr('data-tier', d => d.data.tier || 'no-evidence')
      .classed('is-root', d => d.depth === 0)
      .classed('is-lineage', d => split && d.depth === 1)
      .classed('has-more', d => !!d.data.has_more);

    nodeSel.select('title').text(d =>
      `${d.data.name} — ${d.data.rank}` +
      (d.data.rank !== 'species' ? ` · ${(d.data.n_species || 0).toLocaleString()} species` : '') +
      (d.data.has_more ? ' · click to open' : ''));

    nodeSel.select('path.rad-stub')
      .attr('d', d => d.data.has_more ? 'M0,0 L14,0' : null);

    nodeSel.transition(t)
      .attr('opacity', 1)
      .attr('transform', d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`);

    nodeSel.select('circle.rad-dot').transition(t)
      .attr('r', d => nodeRadius(d));

    /* labels ---------------------------------------------------------------- */
    const labelled = shown.filter(d => !d.children || d.depth === 0);

    // With a few hundred tips the labels would overprint each other. Work out
    // the arc available to each tip and, when it is too tight, keep only the
    // ones that carry evidence -- the rest stay in the DOM at zero opacity so
    // hovering still reveals them.
    const tips = root.leaves().length;
    const arcPer = (TAU * radius) / Math.max(tips, 1);
    const tight = arcPer < 9.5;
    const keep = d => !tight || d.depth === 0 || d.data.profiled ||
      ['established', 'probable', 'possible'].includes(d.data.tier);
    const baseOpacity = d => (d.depth === 0 ? 0 : (keep(d) ? 1 : 0));
    el.classList.toggle('tight-labels', tight);
    svg.classed('tight-labels', tight);

    gLabels.selectAll('text')
      .data(labelled, d => d.data.id)
      .join(
        enter => enter.append('text')
          .attr('class', d => `rad-lab${d.data.rank === 'species' ? ' sp' : ''}`)
          .attr('data-id', d => d.data.id)
          .attr('opacity', 0)
          .attr('transform', d => {
            const p = prevPos.get(d.parent?.data.id) || { x: d.x, y: 0 };
            return labelTransform(p.x, p.y);
          }),
        update => update,
        exit => exit.transition(t).attr('opacity', 0).remove())
      .text(labelOf)
      .attr('text-anchor', d => flipped(d.x) ? 'end' : 'start')
      .attr('data-base-opacity', baseOpacity)
      .style('font-size', tight ? '8.6px' : null)
      .transition(t)
      .attr('opacity', baseOpacity)
      .attrTween('transform', function (d) {
        const from = prevPos.get(d.data.id)
          || prevPos.get(d.parent?.data.id)
          || { x: d.x, y: 0 };
        const i = d3.interpolate(from, { x: d.x, y: d.y });
        return u => { const p = i(u); return labelTransform(p.x, p.y); };
      });

    /* lineage brackets --------------------------------------------------------- */
    // One band per unrelated lineage, sitting inside the first ring. The bands
    // and the gaps between them are the only thing holding a wedge together --
    // there is no stem to the centre, because there is no shared ancestor.
    const bandR = Math.max(26, inner - 16);
    const arcSel = gArcs.selectAll('g.rad-arc')
      .data(lineages, d => d.node.data.id)
      .join(
        enter => {
          const g = enter.append('g').attr('class', 'rad-arc').attr('opacity', 0);
          g.append('path').attr('class', 'rad-arc-band');
          g.append('path').attr('class', 'rad-arc-text').attr('fill', 'none');
          g.append('text').attr('class', 'rad-arc-lab')
            .append('textPath').attr('startOffset', '50%');
          return g;
        },
        update => update,
        exit => exit.transition(t).attr('opacity', 0).remove())
      .attr('data-id', d => d.node.data.id)
      .attr('data-tier', d => d.node.data.tier || 'no-evidence');

    arcSel.select('path.rad-arc-band')
      .attr('data-id', d => d.node.data.id)
      .transition(t)
      .attr('d', d => arcPath(bandR, d.a0, d.a1));

    // The name rides the arc, so it never converges on the centre the way a
    // radial label would. Too short an arc and it is dropped -- the dot still
    // carries the name on hover.
    arcSel.each(function (d) {
      const g = d3.select(this);
      const id = `rad-arcp-${d.node.data.id.replace(/[^\w-]/g, '_')}`;
      const r = bandR + (flipped(d.mid) ? -9 : 11);
      g.select('path.rad-arc-text').attr('id', id).attr('d', arcPath(r, d.a0, d.a1));
      const name = d.node.data.name;
      const fits = d.span * r > name.length * 6.1;
      // SVG2 `href` only: the deprecated xlink:href alongside it produced a
      // duplicate attribute in serialised output, and every browser this app
      // targets resolves the plain href on a textPath.
      g.select('textPath')
        .attr('href', `#${id}`)
        .text(fits ? name : '');
    });

    arcSel.transition(t).attr('opacity', 1);

    /* hub --------------------------------------------------------------------- */
    const r0 = data.nodes[data.root];
    if (split) {
      svg.select('.rad-hub-name').text('No common ancestor');
      svg.select('.rad-hub-sub').text(`${lineages.length} independent lineages`);
    } else {
      svg.select('.rad-hub-name').text(r0.name);
      svg.select('.rad-hub-sub').text(
        `${r0.rank}${r0.n_species ? ` · ${r0.n_species.toLocaleString()} species` : ''}`);
    }

    // The root is deliberately left out of prevPos in split mode: it has no
    // position, so lineages enter radially from the centre instead of from it.
    prevPos = new Map(shown.map(d => [d.data.id, { x: d.x, y: d.y }]));

    el.querySelector('.rad-stat').textContent =
      `${shown.length} nodes · ${root.leaves().length} tips · ${maxDepth} ranks` +
      (split ? ` · ${lineages.length} unrelated lineages` : '');
    renderCrumbs();
  }

  const flipped = x => (x * 180 / Math.PI) % 360 >= 180;

  function labelTransform(x, y) {
    const deg = x * 180 / Math.PI - 90;
    const flip = flipped(x);
    return `rotate(${deg}) translate(${y + 12},0)${flip ? ' rotate(180)' : ''}`;
  }

  function renderCrumbs() {
    const path = data.path || [];
    el.querySelector('.rad-crumbs').innerHTML = path.map((p, i) =>
      `<button type="button" data-root="${esc(p.id)}"${i === path.length - 1 ? ' class="now"' : ''}>${esc(p.name)}</button>`
    ).join('<span class="sep">›</span>');
  }

  /* ---------------------------------------------------------- behaviour */

  function lineage(id) {
    const out = [];
    const nodes = data.nodes;
    let cur = id;
    const parentOf = {};
    Object.values(nodes).forEach(n => (n.children || []).forEach(c => { parentOf[c] = n.id; }));
    while (cur) { out.push(cur); cur = parentOf[cur]; }
    return out;
  }

  function highlight(id) {
    if (!id) {
      el.classList.remove('has-hover');
      svg.selectAll('.lit').classed('lit', false);
      svg.selectAll('.rad-lab')
         .attr('opacity', function () { return +(this.getAttribute('data-base-opacity') ?? 1); });
      tip.hidden = true;
      return;
    }
    const chain = new Set(lineage(id));
    el.classList.add('has-hover');
    svg.selectAll('[data-id]').classed('lit', function () {
      return chain.has(this.getAttribute('data-id'));
    });
    svg.selectAll('.rad-lab').attr('opacity', function () {
      return this.classList.contains('lit')
        ? 1 : +(this.getAttribute('data-base-opacity') ?? 1);
    });
    const n = data.nodes[id];
    if (!n) return;
    tip.hidden = false;
    tip.innerHTML =
      `<b>${esc(n.name)}</b>
       <span>${esc(n.rank)}${n.rank !== 'species'
         ? ` · ${(n.n_species || 0).toLocaleString()} species` : ''}</span>
       ${n.serogroup ? `<span class="tip-sg">${esc(n.serogroup)}</span>` : ''}
       ${n.profiled ? '<em>has a pathogenicity profile</em>' : ''}
       ${n.has_more ? '<em>click to open this branch</em>' : ''}`;
  }

  async function load(id, { animate = true } = {}) {
    if (busy) return;
    busy = true;
    el.classList.add('loading');
    try {
      const url = new URL('api/subtree', document.baseURI);
      url.searchParams.set('id', id);
      url.searchParams.set('depth', depth);
      url.searchParams.set('fan', fan);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`subtree ${res.status}`);
      data = await res.json();
      rootId = id;
      render({ animate });
    } catch (err) {
      el.querySelector('.rad-stat').textContent = `could not load: ${err.message}`;
    } finally {
      busy = false;
      el.classList.remove('loading');
    }
  }

  function attach(host, select) {
    el = host;
    onSelect = select;
    el.innerHTML = `
      <div class="rad-bar">
        <div class="rad-crumbs"></div>
        <div class="rad-ctrl">
          <label>depth<select class="rad-depth">
            ${[2, 3, 4, 5].map(d => `<option${d === depth ? ' selected' : ''}>${d}</option>`).join('')}
          </select></label>
          <label>branches<select class="rad-fan">
            ${[8, 16, 36, 80].map(f => `<option${f === fan ? ' selected' : ''}>${f}</option>`).join('')}
          </select></label>
          <button type="button" class="chip rad-up">↑ up a rank</button>
          <button type="button" class="chip rad-reset">reset view</button>
        </div>
      </div>
      <div class="rad-stage">
        <svg class="rad-svg" role="img" aria-label="Radial taxonomy tree"></svg>
        <div class="rad-tip" hidden></div>
        <div class="rad-spin" aria-hidden="true"></div>
      </div>
      <div class="rad-foot">
        <span class="rad-stat"></span>
        <span class="rad-note">Rings are ICTV ranks, not evolutionary distance —
          a taxonomy, not an inferred phylogeny. At the top level the wedges are
          <b>deliberately disconnected</b>: realms share no demonstrated common
          ancestor, so nothing is joined through the centre. Drag to pan, scroll
          to zoom, click a branch to re-root, click a tip to open it.</span>
      </div>`;

    tip = el.querySelector('.rad-tip');
    svg = d3.select(el).select('.rad-svg')
      .attr('viewBox', [-500, -500, 1000, 1000])
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const defs = svg.append('defs');
    const glow = defs.append('radialGradient').attr('id', 'rad-hub-glow');
    glow.append('stop').attr('offset', '0%').attr('class', 'hub-stop-0');
    glow.append('stop').attr('offset', '100%').attr('class', 'hub-stop-1');

    gRoot = svg.append('g').attr('class', 'rad-root');
    gRings = gRoot.append('g').attr('class', 'rad-rings');
    gArcs = gRoot.append('g').attr('class', 'rad-arcs');
    gLinks = gRoot.append('g').attr('class', 'rad-links');
    gNodes = gRoot.append('g').attr('class', 'rad-nodes');
    gLabels = gRoot.append('g').attr('class', 'rad-labels');

    const hub = gRoot.append('g').attr('class', 'rad-hubg');
    hub.append('circle').attr('class', 'rad-hub-glow').attr('r', 78)
       .attr('fill', 'url(#rad-hub-glow)');
    hub.append('circle').attr('class', 'rad-hub').attr('r', 34);
    hub.append('text').attr('class', 'rad-hub-name').attr('text-anchor', 'middle').attr('y', -1);
    hub.append('text').attr('class', 'rad-hub-sub').attr('text-anchor', 'middle').attr('y', 13);

    zoomBehaviour = d3.zoom()
      .scaleExtent([0.45, 5])
      .on('zoom', ev => gRoot.attr('transform', ev.transform));
    svg.call(zoomBehaviour).on('dblclick.zoom', null);

    svg.on('click', ev => {
      const t = ev.target.closest('[data-id]');
      if (!t) return;
      const id = t.getAttribute('data-id');
      const n = data?.nodes[id];
      if (!n) return;
      if (n.rank === 'species') { onSelect?.(id, { keepView: false }); return; }
      load(id);
      onSelect?.(id, { keepView: true });
    });

    svg.on('mouseover', ev => {
      const t = ev.target.closest('[data-id]');
      if (t) highlight(t.getAttribute('data-id'));
    });
    svg.on('mousemove', ev => {
      if (tip.hidden) return;
      const b = el.querySelector('.rad-stage').getBoundingClientRect();
      tip.style.left = `${ev.clientX - b.left + 14}px`;
      tip.style.top = `${ev.clientY - b.top + 14}px`;
    });
    svg.on('mouseleave', () => highlight(null));

    el.querySelector('.rad-depth').addEventListener('change', e => {
      depth = +e.target.value; load(rootId);
    });
    el.querySelector('.rad-fan').addEventListener('change', e => {
      fan = +e.target.value; load(rootId);
    });
    el.querySelector('.rad-up').addEventListener('click', () => {
      const p = data?.path || [];
      if (p.length > 1) load(p[p.length - 2].id);
    });
    el.querySelector('.rad-reset').addEventListener('click', () => {
      svg.transition().duration(dur()).call(zoomBehaviour.transform, d3.zoomIdentity);
    });
    el.querySelector('.rad-crumbs').addEventListener('click', ev => {
      const b = ev.target.closest('[data-root]');
      if (b) load(b.dataset.root);
    });
  }

  /** Re-root on the nearest ancestor that gives a readable fan-out. */
  function focus(nodeId, path) {
    const ranks = (path || []).map(p => p.rank);
    for (const r of ['genus', 'subfamily', 'family', 'order', 'class']) {
      const i = ranks.lastIndexOf(r);
      if (i >= 0) return load(path[i].id);
    }
    return load(nodeId || 'root');
  }

  /** Light the lineage of a node selected elsewhere, if it is on screen. */
  function reveal(id) {
    if (!data || !data.nodes[id]) return false;
    highlight(id);
    return true;
  }

  return { attach, load, focus, reveal, get rootId() { return rootId; } };
})();

window.Radial = Radial;
