/** summary.js — landing summary page (index.html) */

document.addEventListener('releases-loaded', function (e) {
  const all = e.detail.releases || [];

  // Stats
  const week = all.filter(r => r.days_until_release <= 7);
  document.getElementById('stat-total').textContent = all.length;
  document.getElementById('stat-week').textContent  = week.length;
  document.getElementById('stat-high').textContent  = all.filter(r => r.hype_level === 'HIGH').length;
  document.getElementById('stat-ext').textContent   = all.filter(r => r.hype_level === 'EXTREME').length;

  // Drops Today widget
  const dropsToday = all.filter(r => r.days_until_release === 0);
  if (dropsToday.length) {
    const widget = document.getElementById('drops-today');
    document.getElementById('drops-today-names').innerHTML = dropsToday.map(r => {
      const smCls = window.SRT.saleClass(r.sale_method || 'Online + Retail');
      return `<span class="dt-shoe"><span class="dt-shoe-name">${r.name}</span><span class="sale-badge ${smCls}">${r.sale_method || 'Online + Retail'}</span></span>`;
    }).join('');
    widget.style.display = 'flex';
  }

  // Alert banner
  const imminent = all.filter(r => (r.hype_level === 'HIGH' || r.hype_level === 'EXTREME') && r.days_until_release <= 7);
  if (imminent.length) {
    const b = document.getElementById('alert-banner');
    document.getElementById('alert-text').textContent =
      `${imminent.length} HIGH/EXTREME drop${imminent.length > 1 ? 's' : ''} within 7 days — heightened crowd management expected.`;
    b.classList.add('show');
  }

  // Top Hype Releases (top 6 by score)
  const topHype = [...all].sort((a, b) => b.hype_score - a.hype_score).slice(0, 6);
  const topEl = document.getElementById('top-hype-list');
  if (!topHype.length) {
    topEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.82rem;">No data yet.</div>';
  } else {
    topEl.innerHTML = topHype.map((r, i) => `
<div class="top-release-row">
  <span class="tr-rank">#${i+1}</span>
  <span class="tr-name" title="${r.name}">${r.name}</span>
  <div class="tr-meta">
    <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    ${window.SRT.daysChip(r.days_until_release)}
  </div>
</div>`).join('');
  }

  // This Week
  const weekEl = document.getElementById('this-week-list');
  const weekSorted = week.sort((a, b) => a.release_date.localeCompare(b.release_date));
  if (!weekSorted.length) {
    weekEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.82rem;">No drops this week.</div>';
  } else {
    weekEl.innerHTML = weekSorted.map(r => `
<div class="week-row">
  <span class="wr-date">${window.SRT.formatDateShort(r.release_date)}</span>
  <span class="wr-name" title="${r.name}">${r.name}</span>
  <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
</div>`).join('');
  }

  // Brand Breakdown
  const brandMap = {};
  all.forEach(r => { brandMap[r.brand] = (brandMap[r.brand] || 0) + 1; });
  const brandsSorted = Object.entries(brandMap).sort((a, b) => b[1] - a[1]);
  const maxCount = brandsSorted[0]?.[1] || 1;
  document.getElementById('brand-bars').innerHTML = brandsSorted.map(([brand, count]) => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${brand}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(count/maxCount*100)}%"></div></div>
  <div class="brand-bar-num">${count}</div>
</div>`).join('');
});

// Hype Legend toggle
document.getElementById('legend-toggle').addEventListener('click', function () {
  const body = document.getElementById('legend-body');
  const chev = document.getElementById('legend-chevron');
  const collapsed = body.classList.toggle('collapsed');
  chev.textContent = collapsed ? '▶' : '▼';
});
