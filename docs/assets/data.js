/**
 * data.js — Loads releases.json and exposes it as window.RELEASES_DATA
 * Called before page-specific scripts.
 */
(async function () {
  try {
    const base = (function () {
      // Works locally (file://) and on GitHub Pages (/repo-name/)
      const scripts = document.querySelectorAll('script[src*="data.js"]');
      if (scripts.length) {
        const src = scripts[scripts.length - 1].src;
        return src.replace(/assets\/data\.js.*$/, '');
      }
      return './';
    })();

    const resp = await fetch(base + 'data/releases.json');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const json = await resp.json();

    window.RELEASES_DATA = json;

    // Update last-updated badge on all pages
    const el = document.getElementById('last-updated');
    if (el && json.generated_at) {
      const d = new Date(json.generated_at);
      el.textContent = 'Updated: ' + d.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit', timeZoneName: 'short',
      });
    }

    // Dispatch event so page scripts can react
    document.dispatchEvent(new CustomEvent('releases-loaded', { detail: json }));
  } catch (err) {
    console.error('Failed to load releases.json:', err);
    window.RELEASES_DATA = { total: 0, releases: [] };
    document.dispatchEvent(new CustomEvent('releases-loaded', { detail: window.RELEASES_DATA }));
  }
})();
