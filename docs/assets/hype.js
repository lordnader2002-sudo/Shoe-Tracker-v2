/** hype.js — hype.html */

let viewMode = 'grid';

document.addEventListener('releases-loaded', function (e) {
  const all = e.detail.releases || [];
  const highHype = all.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME')
                      .sort((a,b) => b.hype_score - a.hype_score || a.release_date.localeCompare(b.release_date));

  document.getElementById('stat-extreme').textContent = all.filter(r => r.hype_level === 'EXTREME').length;
  document.getElementById('stat-high').textContent    = all.filter(r => r.hype_level === 'HIGH').length;
  document.getElementById('count-badge').textContent  = highHype.length;

  // Alert banner
  const imminent = highHype.filter(r => r.days_until_release <= 7);
  if (imminent.length) {
    const b = document.getElementById('alert-banner');
    document.getElementById('alert-text').textContent =
      `${imminent.length} HIGH/EXTREME drop${imminent.length>1?'s':''} within 7 days — heightened crowd management expected.`;
    b.classList.add('show');
  }

  // Brand bars
  const brandMap = {};
  highHype.forEach(r => { brandMap[r.brand] = (brandMap[r.brand]||0)+1; });
  const brandsSorted = Object.entries(brandMap).sort((a,b)=>b[1]-a[1]);
  const max = brandsSorted[0]?.[1]||1;
  document.getElementById('brand-bars').innerHTML = brandsSorted.map(([b,n]) => `
<div class="brand-bar-row">
  <div class="brand-bar-label">${b}</div>
  <div class="brand-bar-track"><div class="brand-bar-fill" style="width:${Math.round(n/max*100)}%"></div></div>
  <div class="brand-bar-num">${n}</div>
</div>`).join('');

  renderCards(highHype);
});

function renderCards(list) {
  const c = document.getElementById('releases-container');
  if (!list.length) {
    c.innerHTML = '<div class="cards-grid"><div class="empty-state"><span class="empty-icon">😌</span>No HIGH or EXTREME hype releases in the next 30 days.</div></div>';
    return;
  }
  if (viewMode === 'grid') {
    c.innerHTML = '<div class="cards-grid">' + list.map(r => window.SRT.buildCard(r)).join('') + '</div>';
  } else {
    c.innerHTML = '<div class="list-view">' + window.SRT.listHeader() + list.map(r => window.SRT.buildListRow(r)).join('') + '</div>';
  }
}

document.getElementById('btn-grid')?.addEventListener('click', function () {
  viewMode = 'grid';
  this.classList.add('active');
  document.getElementById('btn-list').classList.remove('active');
  const all = window.RELEASES_DATA?.releases || [];
  renderCards(all.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME').sort((a,b) => b.hype_score - a.hype_score));
});
document.getElementById('btn-list')?.addEventListener('click', function () {
  viewMode = 'list';
  this.classList.add('active');
  document.getElementById('btn-grid').classList.remove('active');
  const all = window.RELEASES_DATA?.releases || [];
  renderCards(all.filter(r => r.hype_level === 'HIGH' || r.hype_level === 'EXTREME').sort((a,b) => b.hype_score - a.hype_score));
});
