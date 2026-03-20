/** calendar.js — calendar.html */

let allReleases = [];
let viewYear, viewMonth;

function buildCalendar() {
  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  document.getElementById('cal-month-label').textContent = MONTHS[viewMonth] + ' ' + viewYear;

  const firstDay    = new Date(viewYear, viewMonth, 1).getDay();
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const today       = new Date();
  const todayKey    = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;

  // Build date → releases map
  const map = {};
  allReleases.forEach(r => {
    const k = r.release_date ? r.release_date.slice(0,10) : null;
    if (!k) return;
    const d = new Date(k + 'T12:00:00');
    if (d.getFullYear() === viewYear && d.getMonth() === viewMonth) {
      (map[k] = map[k] || []).push(r);
    }
  });

  let html = '';
  for (let i = 0; i < firstDay; i++) html += '<div class="cal-day empty"></div>';

  for (let day = 1; day <= daysInMonth; day++) {
    const k = `${viewYear}-${String(viewMonth+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const rels = map[k] || [];
    const isToday = k === todayKey;
    const MAX_SHOWN = 4;
    const entries = rels.slice(0, MAX_SHOWN).map(r => {
      const lvl = (r.hype_level || 'LOW').toLowerCase();
      const dc  = window.SRT.dotClass(r);
      return `<div class="cal-entry ce-${lvl}">
  <span class="cal-entry-dot ${dc}"></span>
  <span class="cal-entry-name" title="${r.name}">${r.name}</span>
</div>`;
    }).join('');
    const moreLabel = rels.length > MAX_SHOWN
      ? `<div class="cal-day-more">+${rels.length - MAX_SHOWN} more</div>` : '';
    html += `<div class="cal-day${isToday?' today':''}${rels.length?' has-releases':''}" data-date="${k}">
  <div class="cal-day-num">${day}</div>
  <div class="cal-day-entries">${entries}</div>
  ${moreLabel}
</div>`;
  }

  const grid = document.getElementById('calendar-grid');
  grid.innerHTML = html;
  grid.querySelectorAll('.cal-day.has-releases').forEach(el => {
    el.addEventListener('click', function () { showDayDetail(this.dataset.date, map[this.dataset.date] || []); });
  });
}

function showDayDetail(dateKey, releases) {
  const d = new Date(dateKey + 'T12:00:00');
  document.getElementById('detail-date-label').textContent =
    d.toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric', year:'numeric' });
  document.getElementById('detail-cards').innerHTML = releases.map(r => window.SRT.buildCard(r)).join('');
  const panel = document.getElementById('day-detail');
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior:'smooth', block:'start' });
}

function initCalendar(data) {
  allReleases = (data && data.releases) || [];
  const today = new Date();
  viewYear = today.getFullYear(); viewMonth = today.getMonth();
  buildCalendar();
}

if (window.RELEASES_DATA) {
  initCalendar(window.RELEASES_DATA);
} else {
  document.addEventListener('releases-loaded', function (e) { initCalendar(e.detail); });
}

document.getElementById('cal-prev').addEventListener('click', function () {
  if (--viewMonth < 0) { viewMonth = 11; viewYear--; }
  buildCalendar(); document.getElementById('day-detail').style.display = 'none';
});
document.getElementById('cal-next').addEventListener('click', function () {
  if (++viewMonth > 11) { viewMonth = 0; viewYear++; }
  buildCalendar(); document.getElementById('day-detail').style.display = 'none';
});
document.getElementById('detail-close').addEventListener('click', function () {
  document.getElementById('day-detail').style.display = 'none';
});
