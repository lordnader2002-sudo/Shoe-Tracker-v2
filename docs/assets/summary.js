/** summary.js — landing summary page (index.html) */

function initSummary(data) {
  const all = (data && data.releases) || [];

  // Stats
  const week = all.filter(r => r.days_until_release <= 7);
  window.SRT.countUp(document.getElementById('stat-total'), all.length);
  window.SRT.countUp(document.getElementById('stat-week'),  week.length);
  window.SRT.countUp(document.getElementById('stat-high'),  all.filter(r => r.hype_level === 'HIGH').length);
  window.SRT.countUp(document.getElementById('stat-ext'),   all.filter(r => r.hype_level === 'EXTREME').length);

  // Combined notice bar — Drops Today + Alert
  const dropsToday = all.filter(r => r.days_until_release === 0);
  const imminent   = all.filter(r => (r.hype_level === 'HIGH' || r.hype_level === 'EXTREME') && r.days_until_release <= 7);
  if (dropsToday.length || imminent.length) {
    const bar = document.getElementById('notice-bar');
    bar.classList.add('show');
    if (dropsToday.length) {
      document.getElementById('drops-today-names').innerHTML = dropsToday.map(r => {
        const smCls = window.SRT.saleClass(r.sale_method || 'Online + Retail');
        return `<span class="dt-shoe"><span class="dt-shoe-name">${r.name}</span><span class="sale-badge ${smCls}">${r.sale_method || 'Online + Retail'}</span></span>`;
      }).join('');
      document.getElementById('nb-drops').classList.add('show');
      bar.classList.add('has-drops');
    }
    if (imminent.length) {
      document.getElementById('alert-text').textContent =
        `${imminent.length} HIGH/EXTREME drop${imminent.length > 1 ? 's' : ''} within 7 days — heightened crowd management expected.`;
      document.getElementById('nb-alert').classList.add('show');
    }
    if (dropsToday.length && imminent.length) {
      document.getElementById('nb-sep').classList.add('show');
    }
  }

  // Top Hype Releases (top 6 by score)
  const topHype = [...all].sort((a, b) => b.hype_score - a.hype_score).slice(0, 6);
  const topEl = document.getElementById('top-hype-list');
  if (!topHype.length) {
    topEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.82rem;">No data yet.</div>';
  } else {
    topEl.innerHTML = topHype.map((r, i) => {
      const smCls = window.SRT.saleClass(r.sale_method || 'Online + Retail');
      const sm    = r.sale_method || 'Online + Retail';
      return `
<div class="top-release-row">
  <span class="tr-rank">#${i+1}</span>
  <span class="tr-name" title="${r.name}">${r.name}</span>
  <div class="tr-meta">
    <span class="sale-badge ${smCls}">${sm}</span>
    <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    ${window.SRT.daysChip(r.days_until_release)}
  </div>
</div>`;
    }).join('');
  }

  // This Week
  const weekEl = document.getElementById('this-week-list');
  const weekSorted = week.sort((a, b) => a.release_date.localeCompare(b.release_date));
  if (!weekSorted.length) {
    weekEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.82rem;">No drops this week.</div>';
  } else {
    weekEl.innerHTML = weekSorted.map(r => {
      const smCls = window.SRT.saleClass(r.sale_method || 'Online + Retail');
      const sm    = r.sale_method || 'Online + Retail';
      return `
<div class="week-row">
  <span class="wr-date">${window.SRT.formatDateShort(r.release_date)}</span>
  <span class="wr-name" title="${r.name}">${r.name}</span>
  <div class="wr-badges">
    <span class="sale-badge ${smCls}">${sm}</span>
    <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
  </div>
</div>`;
    }).join('');
  }

  // New This Week (releases discovered in the past 7 days)
  const newEl = document.getElementById('new-releases-list');
  const generatedAt = data && data.generated_at ? new Date(data.generated_at) : new Date();
  const cutoff = new Date(generatedAt);
  cutoff.setDate(cutoff.getDate() - 7);
  const newReleases = all
    .filter(r => r.date_added && new Date(r.date_added + 'T00:00:00') >= cutoff)
    .sort((a, b) => new Date(b.date_added) - new Date(a.date_added) || b.hype_score - a.hype_score)
    .slice(0, 8);
  if (!newReleases.length) {
    newEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.82rem;">No new releases discovered this week.</div>';
  } else {
    newEl.innerHTML = newReleases.map(r => {
      const smCls = window.SRT.saleClass(r.sale_method || 'Online + Retail');
      const sm    = r.sale_method || 'Online + Retail';
      return `
<div class="new-release-row">
  <span class="nr-date">${window.SRT.formatDateShort(r.release_date)}</span>
  <span class="nr-name" title="${r.name}">${r.name}</span>
  <div class="nr-meta">
    <span class="sale-badge ${smCls}">${sm}</span>
    <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    ${window.SRT.daysChip(r.days_until_release)}
  </div>
</div>`;
    }).join('');
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

  // Sale Method Breakdown
  const smColorMap = {
    'SNKRS App':       'rgba(255,255,255,0.72)',
    'Confirmed App':   '#3b9eff',
    'Raffle':          '#ff9800',
    'Giveaway':        '#43c96a',
    'Online':          '#00bcd4',
    'Online + Retail': '#a78bfa',
    'In-Store':        '#ffc107',
    'Retail':          'rgba(255,255,255,0.28)',
  };
  const saleMap = {};
  all.forEach(r => {
    const m = r.sale_method || 'Online + Retail';
    saleMap[m] = (saleMap[m] || 0) + 1;
  });
  const saleSorted = Object.entries(saleMap).sort((a, b) => b[1] - a[1]);
  const saleMax = saleSorted[0]?.[1] || 1;
  document.getElementById('sale-bars').innerHTML = saleSorted.map(([method, count]) => {
    const color = smColorMap[method] || 'rgba(255,255,255,0.3)';
    return `
<div class="brand-bar-row">
  <div class="brand-bar-label">${method}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(count/saleMax*100)}%;background:${color};"></div></div>
  <div class="brand-bar-num">${count}</div>
</div>`;
  }).join('');

  // Hype Level Breakdown
  const hypeOrder  = ['EXTREME', 'HIGH', 'MEDIUM', 'LOW'];
  const hypeColors = { LOW: '#43c96a', MEDIUM: '#3b9eff', HIGH: '#ff9800', EXTREME: '#e91e63' };
  const hypeCountMap = {};
  all.forEach(r => { hypeCountMap[r.hype_level] = (hypeCountMap[r.hype_level] || 0) + 1; });
  const hypeLevels = hypeOrder.filter(l => hypeCountMap[l]);
  const hypeMax = Math.max(...hypeLevels.map(l => hypeCountMap[l]), 1);
  document.getElementById('hype-bars').innerHTML = hypeLevels.length
    ? hypeLevels.map(level => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${level}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(hypeCountMap[level]/hypeMax*100)}%;background:${hypeColors[level]};"></div></div>
  <div class="brand-bar-num">${hypeCountMap[level]}</div>
</div>`).join('')
    : '<div style="color:var(--text-dim);font-size:0.82rem;">No data.</div>';

  // Price Range Breakdown
  const priceBuckets = [
    { label: 'Under $100', test: p => p < 100,              color: '#43c96a' },
    { label: '$100–$150',  test: p => p >= 100 && p < 150,  color: '#00bcd4' },
    { label: '$150–$200',  test: p => p >= 150 && p < 200,  color: '#3b9eff' },
    { label: '$200–$300',  test: p => p >= 200 && p < 300,  color: '#a78bfa' },
    { label: '$300+',      test: p => p >= 300,              color: '#e91e63' },
  ];
  const priced = all.filter(r => r.retail_price);
  priceBuckets.forEach(b => { b.count = priced.filter(r => b.test(Number(r.retail_price))).length; });
  const priceFilled = priceBuckets.filter(b => b.count > 0);
  const priceMax = Math.max(...priceFilled.map(b => b.count), 1);
  document.getElementById('price-bars').innerHTML = priceFilled.length
    ? priceFilled.map(b => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${b.label}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(b.count/priceMax*100)}%;background:${b.color};"></div></div>
  <div class="brand-bar-num">${b.count}</div>
</div>`).join('')
    : '<div style="color:var(--text-dim);font-size:0.82rem;">No price data.</div>';

  // Release Month Breakdown
  const monthMap = {};
  all.forEach(r => {
    if (!r.release_date) return;
    const d   = new Date(r.release_date + 'T00:00:00');
    const key = d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    if (!monthMap[key]) monthMap[key] = { count: 0, ts: d.getTime() };
    monthMap[key].count++;
  });
  const monthPalette = ['#3b9eff','#a78bfa','#43c96a','#ff9800','#00bcd4','#ffc107','#e91e63','#ff9800'];
  const monthSorted = Object.entries(monthMap).sort((a, b) => a[1].ts - b[1].ts);
  const monthMax = Math.max(...monthSorted.map(([, v]) => v.count), 1);
  document.getElementById('month-bars').innerHTML = monthSorted.length
    ? monthSorted.map(([label, v], i) => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${label}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(v.count/monthMax*100)}%;background:${monthPalette[i % monthPalette.length]};"></div></div>
  <div class="brand-bar-num">${v.count}</div>
</div>`).join('')
    : '<div style="color:var(--text-dim);font-size:0.82rem;">No data.</div>';
}

// Register event listener first, then also check if data already loaded
// (handles both slow-network first load and fast cached reload)
let _summaryDone = false;
function _runSummary(data) {
  if (_summaryDone) return;
  _summaryDone = true;
  initSummary(data);
}
document.addEventListener('releases-loaded', function(e) { _runSummary(e.detail); });
if (window.RELEASES_DATA) _runSummary(window.RELEASES_DATA);
