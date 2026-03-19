/** app.js — releases.html (grid + compact list toggle) */

let allReleases = [];
let activeBrand   = 'all';
let activeHype    = 'all';
let activeUrgency = 'all';
let searchQuery   = '';
let sortMode      = 'date-asc';
let viewMode      = 'list'; // 'grid' | 'list'

function getFiltered() {
  return allReleases.filter(r => {
    if (activeBrand   !== 'all' && r.brand      !== activeBrand)   return false;
    if (activeHype    !== 'all' && r.hype_level  !== activeHype)   return false;
    if (activeUrgency !== 'all' && r.days_until_release > Number(activeUrgency)) return false;
    if (searchQuery && !r.name.toLowerCase().includes(searchQuery)) return false;
    return true;
  });
}

function getSorted(list) {
  const copy = [...list];
  if (sortMode === 'date-asc')  return copy.sort((a,b) => a.release_date.localeCompare(b.release_date));
  if (sortMode === 'date-desc') return copy.sort((a,b) => b.release_date.localeCompare(a.release_date));
  if (sortMode === 'hype-desc') return copy.sort((a,b) => b.hype_score - a.hype_score);
  if (sortMode === 'price-asc') return copy.sort((a,b) => (a.retail_price||9999)-(b.retail_price||9999));
  return copy;
}

function render() {
  const filtered = getSorted(getFiltered());
  document.getElementById('count-badge').textContent = filtered.length;
  const container = document.getElementById('releases-container');

  if (!filtered.length) {
    container.innerHTML = '<div class="cards-grid"><div class="empty-state"><span class="empty-icon">👟</span>No releases match your filters.</div></div>';
    return;
  }

  if (viewMode === 'grid') {
    container.innerHTML = '<div class="cards-grid">' + filtered.map(r => window.SRT.buildCard(r)).join('') + '</div>';
  } else {
    container.innerHTML = '<div class="list-view">' + window.SRT.listHeader() + filtered.map(r => window.SRT.buildListRow(r)).join('') + '</div>';
  }
}

document.addEventListener('releases-loaded', function (e) {
  allReleases = e.detail.releases || [];

  document.getElementById('stat-total').textContent = allReleases.length;
  document.getElementById('stat-week').textContent  = allReleases.filter(r => r.days_until_release <= 7).length;
  document.getElementById('stat-high').textContent  = allReleases.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME').length;

  // Build brand chips
  const brands = [...new Set(allReleases.map(r => r.brand))].sort();
  const chips = document.getElementById('brand-chips');
  brands.forEach(b => {
    const btn = document.createElement('button');
    btn.className = 'chip'; btn.dataset.brand = b; btn.textContent = b;
    chips.appendChild(btn);
  });

  if (!allReleases.length) {
    document.getElementById('releases-container').innerHTML =
      '<div class="cards-grid"><div class="empty-state"><span class="empty-icon">⏳</span>No upcoming releases found. Check back after the next scraper run.</div></div>';
    return;
  }
  render();
});

// Chip clicks
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

document.getElementById('search-input')?.addEventListener('input', function () {
  searchQuery = this.value.toLowerCase().trim(); render();
});
document.getElementById('sort-select')?.addEventListener('change', function () {
  sortMode = this.value; render();
});

// View toggle
document.getElementById('btn-grid')?.addEventListener('click', function () {
  viewMode = 'grid';
  this.classList.add('active');
  document.getElementById('btn-list').classList.remove('active');
  render();
});
document.getElementById('btn-list')?.addEventListener('click', function () {
  viewMode = 'list';
  this.classList.add('active');
  document.getElementById('btn-grid').classList.remove('active');
  render();
});
