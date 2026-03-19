/**
 * calendar.js — Calendar page logic (calendar.html)
 */

let allReleases = [];
let viewYear, viewMonth;

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

function dotClass(r) {
  if (r.hype_level === 'EXTREME') return 'extreme';
  if (r.hype_level === 'HIGH')    return 'high';
  if (r.days_until_release <= 7)  return 'urgent';
  if (r.hype_level === 'MEDIUM')  return 'medium';
  return 'normal';
}

function buildCard(r) {
  const imgHtml = r.image_url
    ? `<img src="${r.image_url}" alt="${r.name}" loading="lazy" onerror="this.parentElement.innerHTML='<span class=card-image-placeholder>👟</span>'" />`
    : `<span class="card-image-placeholder">👟</span>`;
  const price = r.retail_price
    ? `<span class="price-tag">$${Number(r.retail_price).toFixed(0)}</span>`
    : `<span class="price-tbd">TBD</span>`;
  const hypeWidth = Math.round((r.hype_score / 10) * 100);

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
  </div>
</div>`;
}

function buildCalendar() {
  const label = document.getElementById('cal-month-label');
  const grid  = document.getElementById('calendar-grid');

  const monthNames = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];
  label.textContent = monthNames[viewMonth] + ' ' + viewYear;

  const firstDay = new Date(viewYear, viewMonth, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const today = new Date();
  const todayKey = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;

  // Build a map: 'YYYY-MM-DD' -> [releases]
  const releaseMap = {};
  allReleases.forEach(r => {
    const key = r.release_date ? r.release_date.slice(0, 10) : null;
    if (!key) return;
    const d = new Date(key + 'T12:00:00');
    if (d.getFullYear() === viewYear && d.getMonth() === viewMonth) {
      if (!releaseMap[key]) releaseMap[key] = [];
      releaseMap[key].push(r);
    }
  });

  let html = '';

  // Empty cells before month start
  for (let i = 0; i < firstDay; i++) {
    html += '<div class="cal-day empty"></div>';
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const keyDay = `${viewYear}-${String(viewMonth+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const dayReleases = releaseMap[keyDay] || [];
    const isToday = keyDay === todayKey;
    const hasRel = dayReleases.length > 0;

    const dots = dayReleases.slice(0, 8).map(r =>
      `<div class="cal-dot ${dotClass(r)}" title="${r.name}"></div>`
    ).join('');

    const countLabel = dayReleases.length > 1
      ? `<div class="cal-day-count">${dayReleases.length} drops</div>` : '';

    html += `
<div class="cal-day${isToday ? ' today' : ''}${hasRel ? ' has-releases' : ''}" data-date="${keyDay}">
  <div class="cal-day-num">${day}</div>
  <div class="cal-day-dots">${dots}</div>
  ${countLabel}
</div>`;
  }

  grid.innerHTML = html;

  // Click handler for day cells
  grid.querySelectorAll('.cal-day.has-releases').forEach(el => {
    el.addEventListener('click', function () {
      const key = this.dataset.date;
      showDayDetail(key, releaseMap[key] || []);
    });
  });
}

function showDayDetail(dateKey, releases) {
  const panel = document.getElementById('day-detail');
  const dateLabel = document.getElementById('detail-date-label');
  const cards = document.getElementById('detail-cards');

  const d = new Date(dateKey + 'T12:00:00');
  dateLabel.textContent = d.toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric', year:'numeric' });
  cards.innerHTML = releases.map(buildCard).join('');
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.addEventListener('releases-loaded', function (e) {
  allReleases = (e.detail.releases || []);

  const today = new Date();
  viewYear  = today.getFullYear();
  viewMonth = today.getMonth();

  buildCalendar();
});

document.getElementById('cal-prev').addEventListener('click', function () {
  viewMonth--;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  buildCalendar();
  document.getElementById('day-detail').style.display = 'none';
});

document.getElementById('cal-next').addEventListener('click', function () {
  viewMonth++;
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  buildCalendar();
  document.getElementById('day-detail').style.display = 'none';
});

document.getElementById('detail-close').addEventListener('click', function () {
  document.getElementById('day-detail').style.display = 'none';
});
