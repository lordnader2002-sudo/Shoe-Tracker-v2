/**
 * hype.js — Hype Watch page logic (hype.html)
 */

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T12:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function hypeBarColor(level) {
  return { LOW: '#4caf50', MEDIUM: '#2196f3', HIGH: '#ff9800', EXTREME: '#e91e63' }[level] || '#888';
}

function daysChip(days) {
  if (days <= 7)  return `<span class="days-chip days-urgent">${days}d left</span>`;
  if (days <= 14) return `<span class="days-chip days-upcoming">${days}d left</span>`;
  return `<span class="days-chip days-normal">${days}d left</span>`;
}

function buildCard(r) {
  const imgHtml = r.image_url
    ? `<img src="${r.image_url}" alt="${r.name}" loading="lazy" onerror="this.parentElement.innerHTML='<span class=card-image-placeholder>👟</span>'" />`
    : `<span class="card-image-placeholder">👟</span>`;

  const price = r.retail_price
    ? `<span class="price-tag">$${Number(r.retail_price).toFixed(0)}</span>`
    : `<span class="price-tbd">TBD</span>`;

  const emv = r.estimated_market_value
    ? `<span class="meta-pill">EMV $${Number(r.estimated_market_value).toFixed(0)}</span>` : '';

  const hypeWidth = Math.round((r.hype_score / 10) * 100);

  const source = r.source_url
    ? `<a href="${r.source_url}" target="_blank" rel="noopener" class="card-source-link">↗ ${r.source}</a>`
    : `<span class="card-source-link">${r.source}</span>`;

  return `
<div class="sneaker-card ${r.days_until_release <= 7 ? 'urgent-card' : r.days_until_release <= 14 ? 'upcoming-card' : ''}">
  <div class="card-image-wrap">${imgHtml}</div>
  <div class="card-body">
    <div class="card-top">
      <div class="card-name">${r.name}</div>
      <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    </div>
    <div class="card-meta">
      <span class="meta-pill brand-pill">${r.brand}</span>
      ${emv}
    </div>
    <div class="hype-score-bar">
      <div class="hype-bar-bg">
        <div class="hype-bar-fill" style="width:${hypeWidth}%;background:${hypeBarColor(r.hype_level)}"></div>
      </div>
      <span class="hype-score-num">${r.hype_score}/10</span>
    </div>
    <div class="card-footer">
      <div class="release-date-wrap">
        <span class="release-date-label">Release</span>
        <span class="release-date-val">${formatDate(r.release_date)}</span>
      </div>
      ${daysChip(r.days_until_release)}
      ${price}
    </div>
    ${source}
  </div>
</div>`;
}

document.addEventListener('releases-loaded', function (e) {
  const releases = (e.detail.releases || []);

  const highHype = releases.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME');
  highHype.sort((a, b) => b.hype_score - a.hype_score || a.release_date.localeCompare(b.release_date));

  // Stats
  document.getElementById('stat-extreme').textContent = releases.filter(r => r.hype_level === 'EXTREME').length;
  document.getElementById('stat-high').textContent    = releases.filter(r => r.hype_level === 'HIGH').length;
  document.getElementById('count-badge').textContent  = highHype.length;

  // Alert banner for drops within 7 days
  const imminent = highHype.filter(r => r.days_until_release <= 7);
  if (imminent.length) {
    const banner = document.getElementById('alert-banner');
    document.getElementById('alert-text').textContent =
      `${imminent.length} HIGH/EXTREME hype release${imminent.length > 1 ? 's' : ''} within the next 7 days — heightened crowd management recommended.`;
    banner.style.display = 'flex';
  }

  // Brand breakdown bars
  const brandMap = {};
  highHype.forEach(r => { brandMap[r.brand] = (brandMap[r.brand] || 0) + 1; });
  const brandsSorted = Object.entries(brandMap).sort((a, b) => b[1] - a[1]);
  const maxCount = brandsSorted[0]?.[1] || 1;
  const barsEl = document.getElementById('brand-bars');
  barsEl.innerHTML = brandsSorted.map(([brand, count]) => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${brand}</div>
  <div class="brand-bar-track">
    <div class="brand-bar-fill" style="width:${Math.round(count/maxCount*100)}%"></div>
  </div>
  <div class="brand-bar-num">${count}</div>
</div>`).join('');

  // Cards
  const grid = document.getElementById('cards-grid');
  if (!highHype.length) {
    grid.innerHTML = '<div class="empty-state"><span class="empty-icon">😌</span>No HIGH or EXTREME hype releases in the next 30 days.</div>';
    return;
  }
  grid.innerHTML = highHype.map(buildCard).join('');
});
