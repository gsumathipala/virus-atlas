/*! Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
 *  Proprietary. No licence granted; see LICENSE. */
/* Virus Atlas — figure engine.
 *
 * Every figure is an inline SVG built from data: no bitmaps, no external
 * assets, so they stay crisp at any size and recolour with the theme.
 *
 *   virionFigure       labelled particle cross-section, per morphology spec
 *   genomeFigure       genome/segment map with gene blocks
 *   transmissionFigure transmission cycle with organism cartoons
 *   mapFigure          world distribution choropleth
 *   ICON               organism cartoons, shared by the figures
 *
 * Colours come from CSS custom properties (--fig-*) so light and dark themes
 * are handled by the stylesheet rather than here.
 */

const F = (() => {

  const NS = 'http://www.w3.org/2000/svg';
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const r2 = n => Math.round(n * 100) / 100;

  /* ------------------------------------------------------------- organisms */

  // Compact side-on cartoons, each drawn in a 0 0 64 64 box so they can be
  // dropped anywhere at any size. Stroke-based so they inherit theme colour.
  const ICON = {
    mosquito: `<g class="ic">
      <ellipse cx="34" cy="34" rx="11" ry="4.6" transform="rotate(-18 34 34)"/>
      <circle cx="21" cy="29" r="4.4"/>
      <path d="M17 27 6 21M17 30l-10 3"/>
      <path d="M31 28c6-9 17-12 25-9-7 4-14 6-21 11z" class="wing"/>
      <path d="M33 31c7-6 18-6 25-1-8 2-15 2-22 5z" class="wing"/>
      <path d="M28 37l-5 11M34 38l-1 12M40 37l6 10"/>
      <path d="M43 36l6 4"/>
    </g>`,
    midge: `<g class="ic">
      <ellipse cx="32" cy="34" rx="9" ry="6"/>
      <circle cx="21" cy="30" r="4.6"/>
      <path d="M30 28c5-7 15-9 21-6-6 4-12 5-17 9z" class="wing"/>
      <path d="M32 31c6-4 15-3 20 1-7 1-13 1-18 3z" class="wing"/>
      <path d="M27 39l-4 9M33 40v10M39 39l5 9"/>
      <path d="M18 27l-5-4M18 31l-6 1"/>
    </g>`,
    tick: `<g class="ic">
      <ellipse cx="32" cy="35" rx="13" ry="11"/>
      <path d="M32 24v22" class="hair"/>
      <circle cx="32" cy="22" r="4"/>
      <path d="M22 27l-9-6M22 32l-10-2M22 38l-9 4M42 27l9-6M42 32l10-2M42 38l9 4"/>
      <path d="M30 19l-2-5M34 19l2-5"/>
    </g>`,
    sandfly: `<g class="ic">
      <ellipse cx="33" cy="35" rx="10" ry="5.5" transform="rotate(-12 33 35)"/>
      <circle cx="21" cy="31" r="4.2"/>
      <path d="M30 28c6-10 16-13 23-10-7 5-13 7-19 12z" class="wing"/>
      <path d="M17 29l-6-5M17 32l-6 0"/>
      <path d="M28 39l-4 9M34 40l-1 10M40 38l5 9"/>
    </g>`,
    rodent: `<g class="ic">
      <ellipse cx="30" cy="36" rx="15" ry="10"/>
      <circle cx="46" cy="31" r="7"/>
      <circle cx="47" cy="23" r="4"/>
      <circle cx="51" cy="30" r="1.6" class="dot"/>
      <path d="M53 33l6-2M53 35l6 1" class="hair"/>
      <path d="M15 36c-9 2-11 9-5 12" class="tail"/>
      <path d="M24 45v5M34 45v5"/>
    </g>`,
    bat: `<g class="ic">
      <ellipse cx="32" cy="34" rx="5" ry="9"/>
      <circle cx="32" cy="22" r="5"/>
      <path d="M29 18l-3-6 6 3M35 18l3-6-6 3"/>
      <path d="M28 27C20 23 11 24 5 30c7 0 7 6 13 5 4-1 7 2 10 4z" class="wing"/>
      <path d="M36 27c8-4 17-3 23 3-7 0-7 6-13 5-4-1-7 2-10 4z" class="wing"/>
      <path d="M30 43v6M34 43v6"/>
    </g>`,
    pig: `<g class="ic">
      <ellipse cx="30" cy="34" rx="16" ry="11"/>
      <circle cx="47" cy="32" r="8"/>
      <ellipse cx="55" cy="33" rx="4" ry="3.4"/>
      <circle cx="54" cy="33" r="1.2" class="dot"/>
      <path d="M44 24l-2-6 7 3z" class="wing"/>
      <path d="M20 44v6M30 45v5M38 44v6"/>
      <path d="M14 33c-5-1-6 4-2 5" class="tail"/>
    </g>`,
    bird: `<g class="ic">
      <ellipse cx="30" cy="34" rx="14" ry="9" transform="rotate(-12 30 34)"/>
      <circle cx="44" cy="25" r="6"/>
      <path d="M50 24l8 2-8 3z"/>
      <circle cx="46" cy="24" r="1.3" class="dot"/>
      <path d="M24 30c6-5 14-4 18 1-6 4-13 5-19 2z" class="wing"/>
      <path d="M16 38l-11 7 12-1z" class="wing"/>
      <path d="M28 43l-2 7M34 43l1 7"/>
    </g>`,
    human: `<g class="ic">
      <circle cx="32" cy="18" r="7"/>
      <path d="M32 25c-8 0-13 6-13 14v8h26v-8c0-8-5-14-13-14z"/>
      <path d="M22 47v10M42 47v10"/>
    </g>`,
    primate: `<g class="ic">
      <circle cx="32" cy="20" r="8"/>
      <circle cx="22" cy="16" r="4"/><circle cx="42" cy="16" r="4"/>
      <ellipse cx="32" cy="22" rx="4.5" ry="3.5" class="muzzle"/>
      <path d="M32 29c-7 0-12 6-12 13v9h24v-9c0-7-5-13-12-13z"/>
      <path d="M20 40c-6 3-6 10-1 13" class="tail"/>
    </g>`,
    cattle: `<g class="ic">
      <ellipse cx="29" cy="33" rx="17" ry="11"/>
      <circle cx="47" cy="30" r="8"/>
      <path d="M41 22c-3-6 1-8 4-5M53 22c3-6-1-8-4-5"/>
      <circle cx="51" cy="31" r="1.3" class="dot"/>
      <path d="M18 44v7M28 45v6M36 44v7M44 45v6"/>
      <path d="M12 30c-5 2-4 10 1 12" class="tail"/>
    </g>`,
    sheep: `<g class="ic">
      <ellipse cx="29" cy="33" rx="16" ry="11" class="fleece"/>
      <circle cx="45" cy="31" r="7"/>
      <path d="M40 25c-4-4 0-7 3-4" />
      <circle cx="49" cy="31" r="1.3" class="dot"/>
      <path d="M19 43v7M29 44v6M38 43v7"/>
    </g>`,
    horse: `<g class="ic">
      <ellipse cx="28" cy="33" rx="17" ry="10"/>
      <path d="M44 34c2-8 5-12 9-14l3 4-5 5-2 7z"/>
      <circle cx="52" cy="24" r="1.2" class="dot"/>
      <path d="M44 24c3-6 7-8 10-6" class="hair"/>
      <path d="M16 42v9M26 43v8M34 42v9M42 41v10"/>
      <path d="M11 29c-5 1-5 9 0 11" class="tail"/>
    </g>`,
    // A sloth is only legible hanging from a branch, which is also how
    // Oropouche's sylvatic host is usually drawn.
    sloth: `<g class="ic">
      <path d="M5 13h54" class="hair"/>
      <ellipse cx="32" cy="42" rx="12" ry="13"/>
      <circle cx="32" cy="26" r="8"/>
      <circle cx="29" cy="25" r="1.4" class="dot"/><circle cx="35" cy="25" r="1.4" class="dot"/>
      <path d="M30 29q2 2 4 0" class="hair"/>
      <path d="M24 32C18 28 15 20 19 13q3-3 5 1" />
      <path d="M40 32c6-4 9-12 5-19q-3-3-5 1" />
      <path d="M26 54q-4 4-1 7M38 54q4 4 1 7" class="hair"/>
    </g>`,
    cell: `<g class="ic">
      <circle cx="32" cy="32" r="18"/>
      <circle cx="32" cy="32" r="7" class="nucleus"/>
      <path d="M32 14v4M32 46v4M14 32h4M46 32h4" class="hair"/>
    </g>`,
    bacterium: `<g class="ic">
      <rect x="16" y="26" width="32" height="14" rx="7"/>
      <path d="M48 30c7-3 10 1 12 4M48 36c7 3 10 7 12 5" class="hair"/>
      <path d="M16 33h-8" class="hair"/>
    </g>`,
    plant: `<g class="ic">
      <path d="M32 50V22"/>
      <path d="M32 34c-10 0-16-6-16-14 10 0 16 6 16 14z" class="wing"/>
      <path d="M32 28c10 0 16-6 16-14-10 0-16 6-16 14z" class="wing"/>
      <path d="M24 52h16"/>
    </g>`,
    fungus: `<g class="ic">
      <path d="M14 30c0-11 8-18 18-18s18 7 18 18z"/>
      <path d="M26 30c0 10-2 16-4 22h20c-2-6-4-12-4-22"/>
    </g>`,
    archaea: `<g class="ic">
      <path d="M32 12l16 10v20L32 52 16 42V22z"/>
      <circle cx="32" cy="32" r="6" class="nucleus"/>
    </g>`,
    droplet: `<g class="ic">
      <path d="M32 10c8 12 14 19 14 26a14 14 0 0 1-28 0c0-7 6-14 14-26z"/>
    </g>`,
    needle: `<g class="ic">
      <path d="M12 52 44 20"/><path d="M38 14l12 12-6 6-12-12z"/><path d="M12 52l-2-6 6 2z"/>
    </g>`,
  };

  const icon = (name, x, y, size, cls = '') => {
    const g = ICON[name] || ICON.cell;
    const k = size / 64;
    return `<g class="icon ${cls}" transform="translate(${r2(x - size / 2)} ${r2(y - size / 2)}) scale(${r2(k)})">${g}</g>`;
  };

  /* --------------------------------------------------------- virion figure */

  // Spike geometry by type, drawn pointing "up" from the origin then rotated
  // around the particle.
  function spikeShape(type, len) {
    switch (type) {
      case 'club':     // coronavirus-style trumpet
        return `<path class="spk" d="M0 0v${-len * 0.62}" />
                <path class="spk-head" d="M${-len * 0.26} ${-len * 0.62}
                  q${len * 0.26} ${-len * 0.42} ${len * 0.52} 0 z"/>`;
      case 'peplomer': // knob on a stalk
        return `<path class="spk" d="M0 0v${-len * 0.66}"/>
                <circle class="spk-head" cx="0" cy="${-len * 0.78}" r="${len * 0.21}"/>`;
      case 'fringe':   // mimivirus fibre fringe
        return `<path class="spk-hair" d="M0 0v${-len}"/>`;
      case 'fibre':    // adenovirus penton fibre
        return `<path class="spk" d="M0 0v${-len * 0.8}"/>
                <circle class="spk-head" cx="0" cy="${-len * 0.9}" r="${len * 0.14}"/>`;
      case 'spike':
      default:         // trimeric glycoprotein wedge
        return `<path class="spk-head" d="M${-len * 0.2} 0 L0 ${-len} L${len * 0.2} 0 z"/>`;
    }
  }

  function spikeRing(cx, cy, r, type, n, len) {
    if (type === 'none') return '';
    let out = '';
    for (let i = 0; i < n; i++) {
      const a = (i / n) * 360;
      out += `<g transform="translate(${cx} ${cy}) rotate(${r2(a)}) translate(0 ${-r})">
                ${spikeShape(type, len)}</g>`;
    }
    return `<g class="spikes-g">${out}</g>`;
  }

  /** A coiled helical nucleocapsid inside a particle of radius r. */
  function helicalCoil(cx, cy, r, turns = 11) {
    const pts = [];
    const steps = turns * 26;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const ang = t * turns * Math.PI * 2;
      const rad = r * (0.30 + 0.62 * Math.sin(Math.PI * t));
      pts.push([cx + Math.cos(ang) * rad, cy + Math.sin(ang) * rad * 0.74]);
    }
    return `<path class="nuc" d="M${pts.map(p => `${r2(p[0])} ${r2(p[1])}`).join('L')}"/>`;
  }

  /** n separate coiled segments, for segmented genomes. */
  function segmentCoils(cx, cy, r, n) {
    if (n <= 1) return helicalCoil(cx, cy, r);
    const out = [];
    const cols = n <= 3 ? n : Math.ceil(Math.sqrt(n));
    const rows = Math.ceil(n / cols);
    const cw = (r * 1.5) / cols, ch = (r * 1.5) / rows;
    for (let i = 0; i < n; i++) {
      const col = i % cols, row = Math.floor(i / cols);
      const x = cx - (r * 0.75) + cw * (col + 0.5);
      const y = cy - (r * 0.75) + ch * (row + 0.5);
      const rr = Math.min(cw, ch) * 0.52;
      const pts = [];
      for (let s = 0; s <= 40; s++) {
        const t = s / 40, ang = t * 3 * Math.PI * 2;
        const rad = rr * (0.25 + 0.7 * Math.sin(Math.PI * t));
        pts.push(`${r2(x + Math.cos(ang) * rad)} ${r2(y + Math.sin(ang) * rad * 0.8)}`);
      }
      out.push(`<path class="nuc" d="M${pts.join('L')}"/>`);
    }
    return out.join('');
  }

  /** Regular polygon, for icosahedral capsid cross-sections. */
  function polygon(cx, cy, r, sides, rot = -90) {
    const pts = [];
    for (let i = 0; i < sides; i++) {
      const a = (rot + i * 360 / sides) * Math.PI / 180;
      pts.push(`${r2(cx + Math.cos(a) * r)},${r2(cy + Math.sin(a) * r)}`);
    }
    return pts.join(' ');
  }

  /** Capsomer dots across a capsid face, to read as subunits. */
  function capsomers(cx, cy, r, step = 11) {
    let out = '';
    for (let y = -r; y <= r; y += step) {
      const w = Math.sqrt(Math.max(0, r * r - y * y)) * 0.92;
      for (let x = -w; x <= w; x += step) {
        out += `<circle class="cap-dot" cx="${r2(cx + x + (Math.round(y / step) % 2 ? step / 2 : 0))}" cy="${r2(cy + y)}" r="2.1"/>`;
      }
    }
    return out;
  }

  const W = 440, H = 300;      // virion figure canvas
  const CX = 186, CY = 150;

  function bodyFor(spec) {
    const seg = Math.max(1, spec.segments || 1);
    const spikeLen = 15;
    const env = spec.envelope;
    const capsidless = spec.capsid === 'none' && (!spec.nm || !spec.nm[1]);

    switch (spec.shape) {

      case 'spherical':
      case 'pleomorphic': {
        const r = 84;
        const wobble = spec.shape === 'pleomorphic';
        const outline = wobble
          ? `<path class="env" d="${blobPath(CX, CY, r, 9, 0.1)}"/>`
          : `<circle class="env" cx="${CX}" cy="${CY}" r="${r}"/>`;
        const inner = wobble
          ? `<path class="env-in" d="${blobPath(CX, CY, r - 7, 9, 0.1)}"/>`
          : `<circle class="env-in" cx="${CX}" cy="${CY}" r="${r - 7}"/>`;
        const core = spec.capsid === 'icosahedral'
          ? `<polygon class="capsid" points="${polygon(CX, CY, r - 26, 6)}"/>
             ${capsomers(CX, CY, r - 33)}`
          : segmentCoils(CX, CY, r - 22, seg);
        return {
          art: `${spikeRing(CX, CY, r, spec.spikes, 26, spikeLen)}${outline}${inner}${core}`,
          r,
          labels: [
            env && ['Lipid envelope', CX, CY - r + 4, 'up'],
            spec.spikes !== 'none' && ['Glycoprotein spikes', CX + r * 0.72, CY - r * 0.72, 'ne'],
            spec.capsid === 'helical'
              ? [seg > 1 ? `${seg} genome segments` : 'Helical nucleocapsid', CX, CY + r - 24, 'in']
              : ['Icosahedral capsid', CX, CY + r - 24, 'in'],
          ].filter(Boolean),
        };
      }

      case 'icosahedral': {
        const r = 82;
        const art = `
          ${spikeRing(CX, CY, r, spec.spikes, spec.spikes === 'fringe' ? 44 : 12, spec.spikes === 'fringe' ? 22 : 16)}
          <polygon class="capsid" points="${polygon(CX, CY, r, 6)}"/>
          <polygon class="capsid-facet" points="${polygon(CX, CY, r * 0.56, 6, -90)}"/>
          ${capsomers(CX, CY, r * 0.86)}
          <g class="nuc-g">${segmentCoils(CX, CY, r * 0.42, Math.min(seg, 12))}</g>`;
        return {
          art, r,
          labels: [
            ['Icosahedral capsid', CX, CY - r + 2, 'up'],
            spec.spikes === 'fibre' && ['Penton fibres', CX + r * 0.75, CY - r * 0.75, 'ne'],
            spec.spikes === 'fringe' && ['Fibre fringe', CX + r * 0.75, CY - r * 0.75, 'ne'],
            [seg > 1 ? `${seg} genome segments` : 'Genome', CX, CY + r - 16, 'in'],
          ].filter(Boolean),
        };
      }

      case 'bullet': {
        const w = 104, h = 150;
        const x = CX - w / 2, y = CY - h / 2;
        const art = `
          ${spikeRing(CX, CY, 0, 'none', 0, 0)}
          <path class="env" d="M${x} ${y + 54} a${w / 2} 56 0 0 1 ${w} 0 V${y + h} H${x} Z"/>
          <path class="env-in" d="M${x + 7} ${y + 56} a${w / 2 - 7} 50 0 0 1 ${w - 14} 0 V${y + h - 7} H${x + 7} Z"/>
          ${Array.from({ length: 9 }, (_, i) =>
            `<path class="nuc" d="M${x + 14} ${y + 70 + i * 9} H${x + w - 14}"/>`).join('')}
          <g class="spikes-g">${(() => {
            // Spikes sit on the outer surface pointing outward: around the
            // dome along its normal, then down both flanks.
            const domeCy = y + 54, rx = w / 2, ry = 56;
            const out = [];
            for (let i = 0; i <= 10; i++) {
              const a = Math.PI + (i / 10) * Math.PI;           // upper half
              const px = CX + Math.cos(a) * rx;
              const py = domeCy + Math.sin(a) * ry;
              const nx = Math.cos(a) / rx, ny = Math.sin(a) / ry;
              const rot = Math.atan2(ny, nx) * 180 / Math.PI + 90;
              out.push(`<g transform="translate(${r2(px)} ${r2(py)}) rotate(${r2(rot)})">
                          ${spikeShape(spec.spikes, 13)}</g>`);
            }
            for (let i = 1; i <= 5; i++) {
              const py = domeCy + i * ((y + h - domeCy) / 6);
              out.push(`<g transform="translate(${x} ${r2(py)}) rotate(-90)">${spikeShape(spec.spikes, 13)}</g>`);
              out.push(`<g transform="translate(${x + w} ${r2(py)}) rotate(90)">${spikeShape(spec.spikes, 13)}</g>`);
            }
            return out.join('');
          })()}</g>`;
        return {
          art, r: w / 2,
          labels: [
            ['Envelope + G spikes', CX, y + 6, 'up'],
            ['Helical nucleocapsid', CX, y + h - 16, 'in'],
          ],
        };
      }

      case 'filament': {
        // Tube widths live on dedicated classes: a presentation attribute
        // would be overridden by the stylesheet's stroke-width.
        const D = 'M70 236 C70 120 118 64 186 64 C250 64 282 104 282 150';
        const art = `
          <path class="env-tube" d="${D}"/>
          <path class="env-tube-in" d="${D}"/>
          <path class="nuc-tube" d="${D}"/>
          <g class="spikes-g">${Array.from({ length: 16 }, (_, i) => {
            const t = i / 15;
            const p = bezierPoint(t);
            return `<g transform="translate(${r2(p.x)} ${r2(p.y)}) rotate(${r2(p.a + 90)})">
                      ${spikeShape(spec.spikes, 11)}</g>`;
          }).join('')}</g>`;
        return {
          art, r: 15,
          labels: [
            ['Filamentous envelope', 250, 88, 'ne'],
            ['Helical nucleocapsid', 150, 214, 'in'],
          ],
        };
      }

      case 'rod': {
        const x1 = 56, x2 = 316, h = 46;
        const art = `
          <rect class="capsid" x="${x1}" y="${CY - h / 2}" width="${x2 - x1}" height="${h}" rx="6"/>
          ${Array.from({ length: 22 }, (_, i) =>
            `<path class="nuc" d="M${x1 + 8 + i * ((x2 - x1 - 16) / 21)} ${CY - h / 2 + 4}
               v${h - 8}"/>`).join('')}
          <path class="nuc-core" d="M${x1 + 4} ${CY} H${x2 - 4}" stroke-dasharray="6 4"/>`;
        return {
          art, r: h / 2,
          labels: [
            ['Helical protein subunits', CX, CY - h / 2 - 4, 'up'],
            ['RNA threaded through the helix', CX, CY + h / 2 + 22, 'down'],
          ],
        };
      }

      case 'brick': {
        const w = 196, h = 132;
        const x = CX - w / 2, y = CY - h / 2;
        const art = `
          <rect class="env" x="${x}" y="${y}" width="${w}" height="${h}" rx="26"/>
          <rect class="env-in" x="${x + 8}" y="${y + 8}" width="${w - 16}" height="${h - 16}" rx="20"/>
          <path class="capsid" d="M${x + 44} ${CY - 26}
            q${w / 2 - 44} -16 ${w - 88} 0 v52 q${-(w / 2 - 44)} 16 ${-(w - 88)} 0 z"/>
          <ellipse class="lateral" cx="${x + 36}" cy="${CY}" rx="15" ry="26"/>
          <ellipse class="lateral" cx="${x + w - 36}" cy="${CY}" rx="15" ry="26"/>
          <path class="nuc" d="M${x + 62} ${CY} H${x + w - 62}" stroke-dasharray="7 5"/>`;
        return {
          art, r: h / 2,
          labels: [
            ['Outer membrane', CX, y + 4, 'up'],
            ['Dumbbell-shaped core', CX, CY + 48, 'down'],
            ['Lateral bodies', x + 20, CY - 34, 'nw'],
          ],
        };
      }

      case 'phage': {
        const hy = 96, headR = 46;
        const art = `
          <polygon class="capsid" points="${polygon(CX, hy, headR, 6)}"/>
          ${capsomers(CX, hy, headR * 0.8)}
          <path class="nuc" d="M${CX - 22} ${hy - 12} q22 14 44 0 q-22 18 -44 6" stroke-dasharray="5 4"/>
          <rect class="tail" x="${CX - 11}" y="${hy + headR - 4}" width="22" height="74" rx="4"/>
          ${Array.from({ length: 8 }, (_, i) =>
            `<path class="tail-ring" d="M${CX - 11} ${hy + headR + 4 + i * 9} h22"/>`).join('')}
          <rect class="baseplate" x="${CX - 27}" y="${hy + headR + 70}" width="54" height="11" rx="4"/>
          ${[-1, 1].map(s => `
            <path class="fibre" d="M${CX + s * 24} ${hy + headR + 80}
              q${s * 20} 16 ${s * 10} 36"/>
            <path class="fibre" d="M${CX + s * 14} ${hy + headR + 81}
              q${s * 8} 22 ${s * 2} 34"/>`).join('')}`;
        return {
          art, r: headR,
          labels: [
            ['Head: packaged dsDNA', CX, hy - headR + 2, 'up'],
            ['Contractile tail', CX + 34, hy + headR + 30, 'ne'],
            ['Tail fibres — host recognition', CX, hy + headR + 118, 'down'],
          ],
        };
      }

      case 'lemon': {
        const art = `
          <path class="env" d="M${CX} ${CY - 78} C${CX + 62} ${CY - 40} ${CX + 62} ${CY + 40} ${CX} ${CY + 78}
            C${CX - 62} ${CY + 40} ${CX - 62} ${CY - 40} ${CX} ${CY - 78} Z"/>
          <path class="env-in" d="M${CX} ${CY - 66} C${CX + 50} ${CY - 34} ${CX + 50} ${CY + 34} ${CX} ${CY + 66}
            C${CX - 50} ${CY + 34} ${CX - 50} ${CY - 34} ${CX} ${CY - 66} Z"/>
          ${helicalCoil(CX, CY, 40, 7)}
          <g class="spikes-g">${[-16, 0, 16].map(dx =>
            `<path class="fibre" d="M${CX + dx} ${CY + 74} q${dx / 2} 20 ${dx} 30"/>`).join('')}</g>`;
        return {
          art, r: 62,
          labels: [
            ['Lemon-shaped envelope', CX, CY - 78, 'up'],
            ['Terminal fibres', CX, CY + 112, 'down'],
          ],
        };
      }

      case 'bottle': {
        const art = `
          <path class="env" d="M${CX - 16} ${CY - 76} h32 l10 44 q24 20 24 52 v12 h-100 v-12
            q0-32 24-52 z"/>
          <path class="env-in" d="M${CX - 9} ${CY - 68} h18 l9 40 q19 16 19 44 v6 h-74 v-6
            q0-28 19-44 z"/>
          ${helicalCoil(CX, CY + 26, 30, 6)}`;
        return {
          art, r: 50,
          labels: [
            ['Narrow neck', CX, CY - 76, 'up'],
            ['Nucleoprotein core', CX, CY + 86, 'down'],
          ],
        };
      }

      default: {   // capsidless replicon
        const art = `
          <path class="nuc-core" d="M70 170 q40 -56 80 -8 t80 -20 q30 -8 42 24"
                fill="none" stroke-dasharray="none" stroke-width="5"/>
          <circle class="capsid" cx="252" cy="166" r="22"/>
          <text class="fig-in" x="252" y="171" text-anchor="middle">RdRp</text>`;
        return {
          art, r: 20,
          labels: [
            ['Naked RNA — no capsid is ever made', 150, 108, 'up'],
            ['Replicase', 252, 206, 'down'],
          ],
        };
      }
    }
  }

  // Wobbly closed path, for pleomorphic particles.
  function blobPath(cx, cy, r, lobes, amp) {
    const pts = [];
    for (let i = 0; i < lobes * 2; i++) {
      const a = (i / (lobes * 2)) * Math.PI * 2;
      const rr = r * (1 + (i % 2 ? -amp : amp));
      pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
    }
    let d = `M${r2(pts[0][0])} ${r2(pts[0][1])}`;
    for (let i = 0; i < pts.length; i++) {
      const p = pts[(i + 1) % pts.length];
      const c = pts[i];
      d += `Q${r2(c[0] + (p[0] - c[0]) * 0.1)} ${r2(c[1] + (p[1] - c[1]) * 0.1)} ${r2((c[0] + p[0]) / 2)} ${r2((c[1] + p[1]) / 2)}`;
      d += `Q${r2(p[0])} ${r2(p[1])} ${r2(p[0])} ${r2(p[1])}`;
    }
    return d + 'Z';
  }

  // Point + tangent angle along the filament bezier, for spike placement.
  function bezierPoint(t) {
    const P = [[70, 236], [70, 120], [118, 64], [186, 64]];
    const Q = [[186, 64], [250, 64], [282, 104], [282, 150]];
    const seg = t < 0.5 ? P : Q;
    const u = t < 0.5 ? t * 2 : (t - 0.5) * 2;
    const b = (p0, p1, p2, p3, u) => {
      const m = 1 - u;
      return m * m * m * p0 + 3 * m * m * u * p1 + 3 * m * u * u * p2 + u * u * u * p3;
    };
    const d = (p0, p1, p2, p3, u) => {
      const m = 1 - u;
      return 3 * m * m * (p1 - p0) + 6 * m * u * (p2 - p1) + 3 * u * u * (p3 - p2);
    };
    const x = b(seg[0][0], seg[1][0], seg[2][0], seg[3][0], u);
    const y = b(seg[0][1], seg[1][1], seg[2][1], seg[3][1], u);
    const dx = d(seg[0][0], seg[1][0], seg[2][0], seg[3][0], u);
    const dy = d(seg[0][1], seg[1][1], seg[2][1], seg[3][1], u);
    return { x, y, a: Math.atan2(dy, dx) * 180 / Math.PI };
  }

  function labelLayer(labels) {
    const PAD = 9;
    return labels.map(([text, x, y, dir]) => {
      if (dir === 'in') {
        return `<text class="fig-in" x="${r2(x)}" y="${r2(y)}" text-anchor="middle">${esc(text)}</text>`;
      }
      let lx = x, ly = y, tx = x, ty = y, anchor = 'middle';
      if (dir === 'up')   { ly = y - 26; ty = ly - PAD; }
      if (dir === 'down') { ly = y + 26; ty = ly + PAD + 6; }
      if (dir === 'ne')   { lx = x + 42; ly = y - 30; tx = lx + 5; ty = ly - 3; anchor = 'start'; }
      if (dir === 'nw')   { lx = x - 42; ly = y - 30; tx = lx - 5; ty = ly - 3; anchor = 'end'; }
      return `<path class="leader" d="M${r2(x)} ${r2(y)} L${r2(lx)} ${r2(ly)}"/>
              <circle class="leader-dot" cx="${r2(x)}" cy="${r2(y)}" r="2.4"/>
              <text class="fig-lab" x="${r2(tx)}" y="${r2(ty)}" text-anchor="${anchor}">${esc(text)}</text>`;
    }).join('');
  }

  /** Scale bar: how big the particle is, in nm. */
  function scaleBar(spec) {
    const [lo, hi] = spec.nm || [0, 0];
    if (!hi) return '';
    const label = lo === hi ? `${hi} nm` : `${lo}–${hi} nm`;
    return `<g class="scale" transform="translate(300 256)">
        <path d="M0 0h96"/><path d="M0 -5v10"/><path d="M96 -5v10"/>
        <text x="48" y="-10" text-anchor="middle">${esc(label)}</text>
        <text x="48" y="19" text-anchor="middle" class="scale-sub">particle size</text>
      </g>`;
  }

  function virionFigure(spec) {
    const b = bodyFor(spec);
    return `<svg class="fig fig-virion" viewBox="0 0 ${W} ${H}" role="img"
       data-shape="${esc(spec.shape)}"
       aria-label="Schematic cross-section of a ${esc(spec.shape_label)} virus particle">
      <g class="virion">${b.art}</g>
      ${labelLayer(b.labels)}
      ${scaleBar(spec)}
    </svg>`;
  }

  /* --------------------------------------------------------- genome figure */

  // Concrete colours rather than a CSS custom property inside hsl(), so the
  // blocks are coloured identically wherever the SVG is rendered.
  const GENE_HUES = [198, 268, 22, 152, 330, 48, 230, 100];
  const geneFill = i => `hsl(${GENE_HUES[i % GENE_HUES.length]} 72% 58% / 0.30)`;
  const geneLine = i => `hsl(${GENE_HUES[i % GENE_HUES.length]} 72% 62%)`;

  function genomeFigure(spec) {
    const genes = spec.genes && spec.genes.length ? spec.genes : ['genome'];
    const seg = Math.max(1, spec.segments || 1);
    const segmented = seg > 1 && seg <= genes.length;
    const w = 460, rowH = segmented ? 30 : 42, pad = 8;
    const rows = segmented ? genes.map(g => [g]) : [genes];
    const h = pad * 2 + rows.length * rowH + 22;

    const body = rows.map((row, ri) => {
      const y = pad + ri * rowH;
      if (segmented) {
        // One bar per segment, labelled inside: a separate left-hand label
        // just repeated the segment name.
        const [name, desc] = String(row[0]).split('—').map(t => t.trim());
        return `<g class="gen-block">
            <rect x="8" y="${y + 3}" width="${w - 16}" height="${rowH - 7}" rx="3"
                  fill="${geneFill(ri)}" stroke="${geneLine(ri)}" stroke-width="1.2"/>
            <text class="gen-name" x="18" y="${y + rowH / 2 + 3}">${esc(name)}</text>
            ${desc ? `<text class="gen-desc" x="${w - 18}" y="${y + rowH / 2 + 3}"
                       text-anchor="end">${esc(desc)}</text>` : ''}
          </g>`;
      }
      const trackW = w - 16;
      const bw = trackW / row.length;
      return `<rect class="gen-track" x="8" y="${y + 8}" width="${trackW}" height="${rowH - 16}" rx="4"/>
        ${row.map((g, i) => {
          const name = String(g).split('—')[0].trim();
          const desc = String(g).split('—')[1];
          return `<g class="gen-block">
              <rect x="${r2(8 + i * bw + 1.5)}" y="${y + 5}" width="${r2(bw - 3)}" height="${rowH - 10}" rx="3"
                    fill="${geneFill(i)}" stroke="${geneLine(i)}" stroke-width="1.2"/>
              <text class="gen-name" x="${r2(8 + i * bw + bw / 2)}" y="${y + rowH / 2 + 3}"
                    text-anchor="middle">${esc(name)}</text>
              ${desc ? `<title>${esc(name)} — ${esc(desc.trim())}</title>` : ''}
            </g>`;
        }).join('')}`;
    }).join('');

    const kb = spec.kb ? `${spec.kb} ${/DNA/.test(spec.genome || '') ? 'kbp' : 'kb'}` : '';
    return `<svg class="fig fig-genome" viewBox="0 0 ${w} ${h}" role="img"
       aria-label="Genome organisation: ${seg} segment(s)">
      ${body}
      <text class="gen-foot" x="8" y="${h - 6}">${esc(spec.genome || '')}${kb ? ` · ~${esc(kb)}` : ''}${seg > 1 ? ` · ${seg} segments` : ' · monopartite'}</text>
    </svg>`;
  }

  /* --------------------------------------------- transmission cycle figure */

  // Which cartoon to use for a free-text vector or host description.
  const VECTOR_ICONS = [
    [/culicoides|biting midge|midge/i, 'midge', 'Biting midge'],
    [/phlebotomus|sandfl/i, 'sandfly', 'Sandfly'],
    [/ixodes|haemaphysalis|amblyomma|hyalomma|dermacentor|rhipicephalus|\btick/i, 'tick', 'Tick'],
    [/cimex|bat bug/i, 'tick', 'Bat bug'],
    [/aedes|culex|anopheles|mosquito|culiseta|coquillettidia|psorophora|haemagogus|sabethes|ochlerotatus/i, 'mosquito', 'Mosquito'],
  ];
  const HOST_ICONS = [
    [/\bbat|pteropus|rousettus|flying fox|chiropter/i, 'bat', 'Bats'],
    [/rodent|mouse|mice|rat\b|vole|mastomys|peromyscus|calomys|apodemus|myodes|oligoryzomys|chipmunk|squirrel|gerbil/i, 'rodent', 'Rodents'],
    [/\bpig|swine|porcine|boar/i, 'pig', 'Pigs'],
    [/bird|avian|passerine|corvid|ardeid|heron|egret|poultry|myna|duck/i, 'bird', 'Birds'],
    [/primate|monkey|macaque|chimpanz|langur|baboon/i, 'primate', 'Primates'],
    [/cattle|cow|bovine|buffalo|ruminant/i, 'cattle', 'Cattle'],
    [/sheep|goat|caprine|ovine|lamb/i, 'sheep', 'Sheep & goats'],
    [/horse|equine|equid/i, 'horse', 'Horses'],
    [/sloth|bradypus/i, 'sloth', 'Sloths'],
    [/hare|rabbit|lagomorph|hedgehog/i, 'rodent', 'Hares & rabbits'],
    [/deer|cervid|macropod|kangaroo|wallaby/i, 'cattle', 'Deer & macropods'],
    [/\bcat\b|\bdog\b|feline|canine|carnivor/i, 'rodent', 'Carnivores'],
    [/human/i, 'human', 'Humans'],
  ];

  const pickIcon = (text, table, fallback) => {
    for (const [rx, ico, label] of table) if (rx.test(text || '')) return { ico, label };
    return fallback;
  };

  function transmissionFigure(p, meta) {
    const vectorText = (p.vectors || []).join('; ');
    const hasVector = !!vectorText && !/^none/i.test(vectorText);
    const transmission = p.transmission || '';
    const reservoir = p.reservoir || '';

    const w = 520, h = 268;
    const nodes = [];
    const arrows = [];

    const human = { x: 430, y: 92, ico: 'human', label: 'Humans',
                    sub: /dead-end/i.test(reservoir) ? 'dead-end host' : null };

    if (hasVector) {
      const v = pickIcon(vectorText, VECTOR_ICONS, { ico: 'mosquito', label: 'Arthropod vector' });
      const res = pickIcon(reservoir, HOST_ICONS, { ico: 'bird', label: 'Vertebrate host' });
      nodes.push({ x: 84, y: 92, ...res, sub: 'reservoir / amplifying host' });
      nodes.push({ x: 257, y: 186, ...v, sub: 'vector' });
      nodes.push(human);
      arrows.push([84, 92, 257, 186, 'bite'], [257, 186, 84, 92, ''],
                  [257, 186, 430, 92, 'bite']);
      if (/human.*amplif|urban cycle|human[–-]mosquito[–-]human/i.test(transmission)) {
        arrows.push([430, 92, 257, 186, 'amplifies']);
      }
    } else if (/rodent|excreta|aerosolis|inhalation/i.test(transmission)) {
      const res = pickIcon(reservoir, HOST_ICONS, { ico: 'rodent', label: 'Rodent reservoir' });
      nodes.push({ x: 110, y: 110, ...res, sub: 'persistently infected' });
      nodes.push({ x: 268, y: 110, ico: 'droplet', label: 'Aerosolised excreta', sub: 'urine, droppings, dust' });
      nodes.push({ ...human, x: 430, y: 110 });
      arrows.push([110, 110, 268, 110, 'shed'], [268, 110, 430, 110, 'inhaled']);
    } else if (/bat|intermediate host/i.test(transmission + reservoir)) {
      nodes.push({ x: 92, y: 96, ico: 'bat', label: 'Bat reservoir', sub: 'subclinical infection' });
      const inter = /pig|horse|equine|date palm/i.test(transmission)
        ? (/horse|equine/i.test(transmission)
            ? { ico: 'horse', label: 'Horses', sub: 'intermediate host' }
            : { ico: 'pig', label: 'Pigs / contaminated sap', sub: 'intermediate' })
        : { ico: 'droplet', label: 'Contaminated food', sub: 'spillover route' };
      nodes.push({ x: 262, y: 170, ...inter });
      nodes.push({ ...human, x: 436, y: 96 });
      arrows.push([92, 96, 262, 170, 'spillover'], [262, 170, 436, 96, 'contact']);
      if (/person-to-person|nosocomial/i.test(transmission)) {
        // Offset so the arrow runs diagonally; a vertical one put its label
        // straight through the "Humans" caption.
        nodes.push({ x: 474, y: 212, ico: 'human', label: 'Further cases', sub: 'nosocomial spread' });
        arrows.push([474, 212, 436, 96, 'person-to-person', 36]);
      }
    } else if (/respiratory|aerosol|droplet/i.test(transmission)) {
      nodes.push({ x: 110, y: 110, ico: 'human', label: 'Infected person' });
      nodes.push({ x: 268, y: 110, ico: 'droplet', label: 'Respiratory aerosols', sub: 'droplets & aerosol' });
      nodes.push({ x: 430, y: 110, ico: 'human', label: 'Susceptible person' });
      arrows.push([110, 110, 268, 110, 'exhaled'], [268, 110, 430, 110, 'inhaled']);
    } else {
      const res = pickIcon(reservoir || transmission, HOST_ICONS, { ico: 'cell', label: 'Host' });
      nodes.push({ x: 130, y: 110, ...res, sub: 'source' });
      nodes.push({ ...human, x: 390, y: 110 });
      arrows.push([130, 110, 390, 110, 'direct contact']);
    }

    const arrowArt = arrows.map(([x1, y1, x2, y2, label, off = 16], i) => {
      const dx = x2 - x1, dy = y2 - y1;
      const len = Math.hypot(dx, dy) || 1;
      const ux = dx / len, uy = dy / len;
      const gap = 42;
      const sx = x1 + ux * gap, sy = y1 + uy * gap;
      const ex = x2 - ux * gap, ey = y2 - uy * gap;
      const mx = (sx + ex) / 2 - uy * off, my = (sy + ey) / 2 + ux * off;
      return `<path class="flow" d="M${r2(sx)} ${r2(sy)} Q${r2(mx)} ${r2(my)} ${r2(ex)} ${r2(ey)}"
                 marker-end="url(#fig-arrow)"/>
        ${label ? `<text class="flow-lab" x="${r2(mx)}" y="${r2(my - 4)}" text-anchor="middle">${esc(label)}</text>` : ''}`;
    }).join('');

    const nodeArt = nodes.map(n => `
      <g class="cyc-node">
        <circle class="cyc-disc" cx="${n.x}" cy="${n.y}" r="33"/>
        ${icon(n.ico, n.x, n.y, 44)}
        <text class="cyc-lab" x="${n.x}" y="${n.y + 50}" text-anchor="middle">${esc(n.label)}</text>
        ${n.sub ? `<text class="cyc-sub" x="${n.x}" y="${n.y + 64}" text-anchor="middle">${esc(n.sub)}</text>` : ''}
      </g>`).join('');

    return `<svg class="fig fig-cycle" viewBox="0 0 ${w} ${h}" role="img"
       aria-label="Transmission cycle">
      <defs><marker id="fig-arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path class="arrowhead" d="M0 0 L10 5 L0 10 z"/></marker></defs>
      ${arrowArt}${nodeArt}
    </svg>`;
  }

  /* ------------------------------------------------------------ map figure */

  let WORLD = null;

  async function world() {
    if (!WORLD) {
      // Absolute, so the fetch works regardless of the current document path.
      // Resolved against the document base, not the origin: the app is
      // served from a subpath on GitHub Pages, and an origin-relative
      // path there fetches the site's 404 page instead of the map.
      const r = await fetch(new URL('static/data/world.json', document.baseURI));
      WORLD = await r.json();
    }
    return WORLD;
  }

  function mapFigure(w, countries, { worldwide = false } = {}) {
    const set = new Set(countries);
    const paths = [];
    const marks = [];
    for (const [name, geom] of Object.entries(w.countries)) {
      if (name === 'Antarctica') continue;
      const on = set.has(name);
      paths.push(`<path class="geo${on ? ' on' : ''}" d="${geom.d}">
        ${on ? `<title>${esc(name)}</title>` : ''}</path>`);
      if (on && geom.c && set.size <= 12) {
        marks.push(`<circle class="geo-dot" cx="${geom.c[0]}" cy="${geom.c[1]}" r="3.4"/>`);
      }
    }
    return `<svg class="fig fig-map" viewBox="0 30 1000 440" role="img"
       aria-label="World distribution map highlighting ${countries.length} countries">
      <g class="geo-g">${paths.join('')}</g>${marks.join('')}
      ${worldwide ? '<text class="map-note" x="500" y="60" text-anchor="middle">reported worldwide</text>' : ''}
    </svg>`;
  }

  /* ----------------------------------------------------------- small charts */

  /** Horizontal stacked bar of evidence tiers, with counts. */
  function tierBar(tiers, order, labels, total) {
    if (!total) return '';
    const present = order.filter(t => tiers[t]);
    let x = 0;
    const segs = present.map(t => {
      const wpc = tiers[t] / total * 100;
      const s = `<rect class="tb" data-tier="${t}" x="${r2(x)}" y="0" width="${r2(wpc)}" height="10" rx="2">
          <title>${esc(labels[t].label)}: ${tiers[t]}</title></rect>`;
      x += wpc;
      return s;
    }).join('');
    return `<svg class="fig fig-tierbar" viewBox="0 0 100 10" preserveAspectRatio="none"
      role="img" aria-label="Distribution of evidence tiers">${segs}</svg>`;
  }

  /** Host-range badges with cartoons. */
  function hostStrip(hosts) {
    const map = {
      Vertebrates: ['human', 'vertebrates'], Invertebrates: ['mosquito', 'invertebrates'],
      Plants: ['plant', 'plants'], Fungi: ['fungus', 'fungi'],
      Bacteria: ['bacterium', 'bacteria'], Archaea: ['archaea', 'archaea'],
      Protists: ['cell', 'protists'], Algae: ['plant', 'algae'],
    };
    return (hosts || []).map(hname => {
      const [ico, label] = map[hname] || ['cell', hname.toLowerCase()];
      return `<span class="host-chip">
          <svg viewBox="0 0 64 64" class="host-ico" aria-hidden="true">${ICON[ico]}</svg>
          ${esc(hname)}</span>`;
    }).join('');
  }

  return { virionFigure, genomeFigure, transmissionFigure, mapFigure, world,
           tierBar, hostStrip, icon, ICON };
})();

// `const` at script scope is not a window property; expose it so the figures
// can be driven from the console and from tests.
window.F = F;
