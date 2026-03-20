/** transitions.js — page fade-out on nav link click */

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
