/** transitions.js — page fade-out on nav link click + light/dark theme toggle */

document.querySelectorAll('.nav-links a').forEach(function(link) {
  link.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) return;
    if (this.classList.contains('active')) return;
    e.preventDefault();
    document.body.classList.add('is-leaving');
    const dest = href;
    setTimeout(function() { window.location.href = dest; }, 130);
  });
});

// ── Theme toggle ──────────────────────────────
(function() {
  var STORAGE_KEY = 'srt-theme';
  var root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = theme === 'light' ? '🌙' : '☀️';
    localStorage.setItem(STORAGE_KEY, theme);
  }

  // Initialise on load (default = dark)
  var saved = localStorage.getItem(STORAGE_KEY) || 'dark';
  applyTheme(saved);

  // Wire up button
  var btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.addEventListener('click', function() {
      applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });
  }
}());
