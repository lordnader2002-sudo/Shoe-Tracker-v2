/**
 * app.js — Main dashboard page logic (index.html)
 */

// ── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T12:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function daysChip(days) {
  if (days <= 7)  return `<span class="days-chip days-urgent">${days}d left</span>`;
  if (days <= 14) return `<span class="days-chip days-upcoming">${days}d left</span>`;
  return `<span class="days-chip days-normal">${days}d left</span>`;
}

function hypeBarColor(level) {
  return { LOW: '#4caf50', MEDIUM: '#2196f3', HIGH: '#ff9800', EXTREME: '#e91e63' }[level] || '#888';
}

function buildCard(r) {
  const urgent   = r.days_until_release <= 7;
  const upcoming = r.days_until_release <= 14 && !urgent;
  const cardClass = urgent ? 'urgent-card' : upcoming ? 'upcoming-card' : '';

  const imgHtml = r.image_url
    ? `<img src="${r.image_url}" alt="${r.name}" loading="lazy" onerror="this.parentElement.innerHTML='<span class=card-image-placeholder>👟</span>'" />`
    : `<span class="card-image-placeholder">👟</span>`;

  const price = r.retail_price
    ? `<span class="price-tag">$${Number(r.retail_price).toFixed(0)}</span>`
    : `<span class="price-tbd">TBD</span>`;

  const emv = r.estimated_market_value
    ? `<span class="meta-pill">EMV $${Number(r.estimated_market_value).toFixed(0)}</span>`
    : '';

  const colorway = r.colorway && r.colorway !== 'N/A'
    ? `<span class="meta-pill">${r.colorway}</span>` : '';
  const styleCode = r.style_code && r.style_code !== 'N/A'
    ? `<span class="meta-pill">${r.style_code}</span>` : '';
  const source = r.source_url
    ? `<a href="${r.source_url}" target="_blank" rel="noopener" class="card-source-link">↗ ${r.source}</a>`
    : `<span class="card-source-link">${r.source}</span>`;

  const hypeWidth = Math.round((r.hype_score / 10) * 100);

  return `
<div class="sneaker-card ${cardClass}">
  <div class="card-image-wrap">${imgHtml}</div>
  <div class="card-body">
    <div class="card-top">
      <div class="card-name">${r.name}</div>
      <span class="hype-badge hype-${r.hype_level}">${r.hype_level}</span>
    </div>
    <div class="card-meta">
      <span class="meta-pill brand-pill">${r.brand}</span>
      ${colorway}${styleCode}${emv}
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

// ── State ─────────────────────────────────────────────────────────────────────

let allReleases = [];
let activeBrand = 'all';
let activeHype  = 'all';
let activeUrgency = 'all';
let searchQuery = '';
let sortMode = 'date-asc';

function getFiltered() {
  return allReleases.filter(r => {
    if (activeBrand !== 'all' && r.brand !== activeBrand) return false;
    if (activeHype  !== 'all' && r.hype_level !== activeHype)  return false;
    if (activeUrgency !== 'all') {
      if (r.days_until_release > Number(activeUrgency)) return false;
    }
    if (searchQuery && !r.name.toLowerCase().includes(searchQuery)) return false;
    return true;
  });
}

function getSorted(list) {
  const copy = [...list];
  if (sortMode === 'date-asc')   return copy.sort((a,b) => a.release_date.localeCompare(b.release_date));
  if (sortMode === 'date-desc')  return copy.sort((a,b) => b.release_date.localeCompare(a.release_date));
  if (sortMode === 'hype-desc')  return copy.sort((a,b) => b.hype_score - a.hype_score);
  if (sortMode === 'price-asc')  return copy.sort((a,b) => (a.retail_price||9999) - (b.retail_price||9999));
  return copy;
}

function render() {
  const filtered = getSorted(getFiltered());
  const grid = document.getElementById('cards-grid');
  document.getElementById('count-badge').textContent = filtered.length;

  if (!filtered.length) {
    grid.innerHTML = '<div class="empty-state"><span class="empty-icon">👟</span>No releases match your filters.</div>';
    return;
  }
  grid.innerHTML = filtered.map(buildCard).join('');
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('releases-loaded', function (e) {
  const data = e.detail;
  allReleases = data.releases || [];

  // Stats
  document.getElementById('stat-total').textContent = allReleases.length;
  document.getElementById('stat-urgent').textContent = allReleases.filter(r => r.days_until_release <= 7).length;
  document.getElementById('stat-high').textContent   = allReleases.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME').length;

  // Build brand chips
  const brands = [...new Set(allReleases.map(r => r.brand))].sort();
  const chipsEl = document.getElementById('brand-chips');
  brands.forEach(b => {
    const btn = document.createElement('button');
    btn.className = 'chip';
    btn.dataset.brand = b;
    btn.textContent = b;
    chipsEl.appendChild(btn);
  });

  // No data message
  if (!allReleases.length) {
    document.getElementById('cards-grid').innerHTML =
      '<div class="empty-state"><span class="empty-icon">⏳</span>No upcoming releases found. The scraper will update this data on the next scheduled run (Mon & Fri @ 01:00 EST).</div>';
    document.getElementById('count-badge').textContent = '0';
    document.getElementById('stat-total').textContent  = '0';
    document.getElementById('stat-urgent').textContent = '0';
    document.getElementById('stat-high').textContent   = '0';
    return;
  }

  render();
});

// ── Filter event handlers ─────────────────────────────────────────────────────

document.addEventListener('click', function (e) {
  const chip = e.target.closest('.chip');
  if (!chip) return;

  if ('brand' in chip.dataset) {
    activeBrand = chip.dataset.brand;
    document.querySelectorAll('[data-brand]').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    render();
  }
  if ('hype' in chip.dataset) {
    activeHype = chip.dataset.hype;
    document.querySelectorAll('[data-hype]').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    render();
  }
  if ('urgency' in chip.dataset) {
    activeUrgency = chip.dataset.urgency;
    document.querySelectorAll('[data-urgency]').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    render();
  }
});

const searchInput = document.getElementById('search-input');
if (searchInput) {
  searchInput.addEventListener('input', function () {
    searchQuery = this.value.toLowerCase().trim();
    render();
  });
}

const sortSelect = document.getElementById('sort-select');
if (sortSelect) {
  sortSelect.addEventListener('change', function () {
    sortMode = this.value;
    render();
  });
}
