/**
 * data.js — Loads releases.json, exposes window.RELEASES_DATA,
 * and provides shared card/list builder utilities.
 */
(async function () {
  // Resolve base URL regardless of deploy path
  const base = (function () {
    const s = document.querySelector('script[src*="data.js"]');
    return s ? s.src.replace(/assets\/data\.js.*$/, '') : './';
  })();

  try {
    const resp = await fetch(base + 'data/releases.json');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    window.RELEASES_DATA = await resp.json();
  } catch (e) {
    console.error('Failed to load releases.json:', e);
    window.RELEASES_DATA = { total: 0, releases: [], generated_at: null };
  }

  // ── Last Updated (EST, 24-hr) ──────────────────────────────────────────
  const el = document.getElementById('last-updated');
  if (el && window.RELEASES_DATA.generated_at) {
    const d = new Date(window.RELEASES_DATA.generated_at);
    el.textContent = 'Updated: ' + d.toLocaleString('en-US', {
      timeZone: 'America/New_York',
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
    }) + ' EST';
  }

  document.dispatchEvent(new CustomEvent('releases-loaded', { detail: window.RELEASES_DATA }));
})();

// ── Shared Utilities ───────────────────────────────────────────────────────

window.SRT = {
  formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso + 'T12:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  },

  formatDateShort(iso) {
    if (!iso) return '—';
    const d = new Date(iso + 'T12:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  },

  hypeColor(level) {
    return { LOW: '#43c96a', MEDIUM: '#3b9eff', HIGH: '#ff9800', EXTREME: '#e91e63' }[level] || '#888';
  },

  daysChip(days) {
    if (days <= 7)  return `<span class="days-chip days-urgent">${days}d</span>`;
    if (days <= 14) return `<span class="days-chip days-upcoming">${days}d</span>`;
    return `<span class="days-chip days-normal">${days}d</span>`;
  },

  dotClass(r) {
    if (r.hype_level === 'EXTREME') return 'd-extreme';
    if (r.hype_level === 'HIGH')    return 'd-high';
    if (r.hype_level === 'MEDIUM')  return 'd-medium';
    if (r.hype_level === 'LOW')     return 'd-low';
    return 'd-low';
  },

  buildCard(r) {
    const urgent   = r.days_until_release <= 7;
    const upcoming = !urgent && r.days_until_release <= 14;
    const cls = urgent ? 'urgent-card' : upcoming ? 'upcoming-card' : '';
    const img = r.image_url
      ? `<img src="${r.image_url}" alt="${r.name}" loading="lazy" onerror="this.parentElement.innerHTML='<span class=card-image-placeholder>👟</span>'" />`
      : `<span class="card-image-placeholder">👟</span>`;
    const price = r.retail_price
      ? `<span class="price-tag">$${Number(r.retail_price).toFixed(0)}</span>`
      : `<span class="price-tbd">TBD</span>`;
    const colorway = r.colorway && r.colorway !== 'N/A' ? `<span class="meta-pill">${r.colorway}</span>` : '';
    const style    = r.style_code && r.style_code !== 'N/A' ? `<span class="meta-pill">${r.style_code}</span>` : '';
    const src = r.source_url
      ? `<a href="${r.source_url}" target="_blank" rel="noopener" class="card-source-link">↗ ${r.source}</a>`
      : `<span class="card-source-link">${r.source || ''}</span>`;
    const barW  = Math.round((r.hype_score / 10) * 100);
    const col   = window.SRT.hypeColor(r.hype_level);
    const method = r.sale_method || 'Online + Retail';
    const smCls  = window.SRT.saleClass(method);
    return `
<div class="sneaker-card ${cls}">
  <div class="card-image-wrap">${img}</div>
  <div class="card-body">
    <div class="card-top">
      <div class="card-name">${r.name}</div>
      <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    </div>
    <div class="card-meta">
      <span class="meta-pill brand-pill">${r.brand}</span>${colorway}${style}
    </div>
    <div class="card-sale-row"><span class="sale-badge ${smCls}">${method}</span></div>
    <div class="hype-score-bar">
      <div class="hype-bar-bg"><div class="hype-bar-fill" style="width:${barW}%;background:${col}"></div></div>
      <span class="hype-score-num">${r.hype_score}/10</span>
    </div>
    <div class="card-footer">
      <div class="release-date-wrap">
        <span class="release-date-label">Release</span>
        <span class="release-date-val">${window.SRT.formatDate(r.release_date)}</span>
      </div>
      ${window.SRT.daysChip(r.days_until_release)}
      ${price}
    </div>
    ${src}
  </div>
</div>`;
  },

  saleClass(method) {
    const map = {
      'SNKRS App':       'sm-snkrs',
      'Confirmed App':   'sm-confirmed',
      'Raffle/Dropship': 'sm-raffle',
      'Giveaway':        'sm-giveaway',
      'Online':          'sm-online',
      'Online + Retail': 'sm-online-retail',
      'In-Store':        'sm-instore',
      'Retail':          'sm-retail',
    };
    return map[method] || 'sm-retail';
  },

  buildListRow(r) {
    const urgent   = r.days_until_release <= 7;
    const upcoming = !urgent && r.days_until_release <= 14;
    const rowCls = urgent ? 'list-row urgent-row' : upcoming ? 'list-row upcoming-row' : 'list-row';
    const dotCls  = window.SRT.dotClass(r);
    const daysCls = urgent ? 'urgent' : upcoming ? 'upcoming' : '';
    const price   = r.retail_price ? `$${Number(r.retail_price).toFixed(0)}` : '—';
    const method  = r.sale_method || 'Online + Retail';
    const smCls   = window.SRT.saleClass(method);
    const link    = r.source_url
      ? `<a href="${r.source_url}" target="_blank" rel="noopener" class="list-link">↗</a>`
      : '<span class="list-link">—</span>';
    return `
<div class="${rowCls}">
  <span class="list-dot ${dotCls}"></span>
  <span class="list-name" title="${r.name}">${r.name}</span>
  <span class="list-brand">${r.brand}</span>
  <span class="sale-badge ${smCls}">${method}</span>
  <span class="list-date">${window.SRT.formatDateShort(r.release_date)}</span>
  <span class="list-days ${daysCls}">${r.days_until_release}d</span>
  <span class="list-price">${price}</span>
  <span class="list-score">${r.hype_score}/10</span>
  ${link}
</div>`;
  },

  listHeader() {
    return `<div class="list-header"><span></span><span>Name</span><span>Brand</span><span>Sale Method</span><span>Date</span><span>Days</span><span>Price</span><span>Score</span><span></span></div>`;
  },

  // Animated count-up for stat numbers
  countUp(el, target, duration) {
    target = parseInt(target, 10) || 0;
    if (!el) return;
    if (target === 0) { el.textContent = '0'; return; }
    duration = duration || 680;
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(ease * target);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  },
};
