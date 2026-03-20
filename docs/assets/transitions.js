/** transitions.js — page transitions + shared animation utilities */

// ── Page fade-out on nav link click ─────────────────────────────────────────
document.querySelectorAll('.nav-links a').forEach(function(link) {
  link.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    // Skip: external links, anchors, already active page
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) return;
    if (this.classList.contains('active')) return;
    e.preventDefault();
    document.body.classList.add('is-leaving');
    const dest = href;
    setTimeout(function() { window.location.href = dest; }, 190);
  });
});

// ── Count-up utility ─────────────────────────────────────────────────────────
// Usage: window.SRT.countUp(element, targetNumber [, durationMs])
window.SRT = window.SRT || {};
window.SRT.countUp = function(el, target, duration) {
  target = parseInt(target, 10) || 0;
  if (target === 0) { el.textContent = '0'; return; }
  duration = duration || 680;
  var start = performance.now();
  function step(now) {
    var progress = Math.min((now - start) / duration, 1);
    // ease-out cubic
    var ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(ease * target);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
};
