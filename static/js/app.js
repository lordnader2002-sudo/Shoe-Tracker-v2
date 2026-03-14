/**
 * Sneaker Release Tracker — Frontend JS
 * Handles: filtering, sorting, card rendering, refresh, Excel export, legend modal
 */

"use strict";

// ============================================================
// State
// ============================================================
const state = {
  releases:     [],
  brands:       [],
  saleMethods:  [],
  stats:        null,
  loading:      false,
};

// ============================================================
// DOM references
// ============================================================
const $ = id => document.getElementById(id);

const dom = {
  loader:       $("loader"),
  emptyState:   $("emptyState"),
  cardsGrid:    $("cardsGrid"),
  searchInput:  $("searchInput"),
  brandFilter:  $("brandFilter"),
  hypeLow:      $("hypeLow"),
  hypeHigh:     $("hypeHigh"),
  methodFilter: $("methodFilter"),
  sortBy:       $("sortBy"),
  clearFilters: $("clearFilters"),
  refreshBtn:   $("refreshBtn"),
  exportBtn:    $("exportBtn"),
  legendBtn:    $("legendBtn"),
  legendModal:  $("legendModal"),
  legendClose:  $("legendClose"),
  toast:        $("toast"),
  lastUpdated:  $("lastUpdated"),
  totalBadge:   $("totalBadge"),
  statTotal:    $("stat-total"),
  statUpcoming: $("stat-upcoming"),
  statGrail:    $("stat-grail"),
  statShowing:  $("stat-showing"),
};

// ============================================================
// Hype helpers
// ============================================================
const HYPE_LABEL = {
  1: "⚪ General Release",
  2: "🟡 Popular",
  3: "🟠 Hyped",
  4: "🔴 Limited",
  5: "🟣 Grail",
};

const HYPE_CLASS = { 1: "hype-1", 2: "hype-2", 3: "hype-3", 4: "hype-4", 5: "hype-5" };
const HYPE_TEXT  = { 1: "hype-1-text", 2: "hype-2-text", 3: "hype-3-text", 4: "hype-4-text", 5: "hype-5-text" };

function hypeStars(n) {
  return "★".repeat(n) + "☆".repeat(5 - n);
}

// ============================================================
// Brand badge helpers
// ============================================================
function brandClass(brand) {
  const map = {
    "Jordan":         "brand-Jordan",
    "Nike":           "brand-Nike",
    "Adidas":         "brand-Adidas",
    "Adidas (Yeezy)": "brand-Adidas-Yeezy",
    "New Balance":    "brand-New-Balance",
    "Puma":           "brand-Puma",
    "Under Armour":   "brand-Under-Armour",
  };
  return map[brand] || "brand-Other";
}

// ============================================================
// Method chip helpers
// ============================================================
function methodChipClass(method) {
  const m = method.toLowerCase();
  if (m.includes("snkrs"))     return "method-chip method-chip--snkrs";
  if (m.includes("raffle"))    return "method-chip method-chip--raffle";
  if (m.includes("draw"))      return "method-chip method-chip--draw";
  if (m.includes("confirmed")) return "method-chip method-chip--confirmed";
  if (m.includes("online"))    return "method-chip method-chip--online";
  return "method-chip";
}

// ============================================================
// Card renderer
// ============================================================
function buildCard(rel) {
  const hype   = rel.hype_level || 1;
  const brand  = rel.brand || "Other";
  const price  = rel.price ? `$${Math.round(rel.price)}` : "TBD";
  const date   = rel.release_date && rel.release_date !== "TBD"
                   ? formatDate(rel.release_date)
                   : "TBD";

  const dateClass  = date === "TBD" ? "card__meta-value card__meta-value--tbd"
                                    : "card__meta-value card__meta-value--date";
  const priceClass = rel.price ? "card__meta-value card__meta-value--price"
                                : "card__meta-value card__meta-value--tbd";

  // Image
  let imgHtml = `<div class="card__image-placeholder">👟</div>`;
  if (rel.image_url) {
    imgHtml = `<img src="${escHtml(rel.image_url)}"
                    alt="${escHtml(rel.name)}"
                    loading="lazy"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
               <div class="card__image-placeholder" style="display:none">👟</div>`;
  }

  // Methods chips (max 4 to avoid overflow)
  const methodsHtml = (rel.sale_methods || [])
    .slice(0, 4)
    .map(m => `<span class="${methodChipClass(m)}">${escHtml(m)}</span>`)
    .join("");

  const sourceName = (() => {
    try {
      return new URL(rel.source_url || "").hostname.replace(/^www\./, "");
    } catch { return rel.source || "Source"; }
  })();

  const card = document.createElement("div");
  card.className = "card";
  card.dataset.hype = hype;

  card.innerHTML = `
    <div class="card__image-wrap">
      ${imgHtml}
      <div class="card__hype-overlay">
        <span class="hype-badge ${HYPE_CLASS[hype]}">${hypeStars(hype)} ${hype}/5</span>
      </div>
      <div class="card__brand-overlay">
        <span class="brand-badge ${brandClass(brand)}">${escHtml(brand)}</span>
      </div>
    </div>

    <div class="card__body">
      <div class="card__name">${escHtml(rel.name || "Unknown Sneaker")}</div>

      <div class="card__meta">
        <div class="card__meta-item">
          <span class="card__meta-key">📅 Release</span>
          <span class="${dateClass}">${date}</span>
        </div>
        <div class="card__meta-item">
          <span class="card__meta-key">💰 Retail</span>
          <span class="${priceClass}">${price}</span>
        </div>
      </div>

      <div class="card__hype-row">
        <span class="hype-stars ${HYPE_TEXT[hype]}">${hypeStars(hype)}</span>
        <span class="hype-label-text ${HYPE_TEXT[hype]}">${HYPE_LABEL[hype]}</span>
      </div>

      <div class="card__methods">${methodsHtml}</div>
    </div>

    <div class="card__footer">
      <a class="card__source-link"
         href="${escHtml(rel.source_url || "#")}"
         target="_blank"
         rel="noopener noreferrer">
        🔗 ${escHtml(sourceName)}
      </a>
      <a class="card__view-btn"
         href="${escHtml(rel.source_url || "#")}"
         target="_blank"
         rel="noopener noreferrer">
        View →
      </a>
    </div>
  `;

  return card;
}

function formatDate(dateStr) {
  try {
    const d = new Date(dateStr + "T00:00:00");  // avoid timezone shift
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch { return dateStr; }
}

function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ============================================================
// Render
// ============================================================
function render(releases) {
  dom.cardsGrid.innerHTML = "";

  if (releases.length === 0) {
    dom.cardsGrid.classList.add("hidden");
    dom.emptyState.classList.remove("hidden");
  } else {
    dom.emptyState.classList.add("hidden");
    dom.cardsGrid.classList.remove("hidden");
    const frag = document.createDocumentFragment();
    releases.forEach(r => frag.appendChild(buildCard(r)));
    dom.cardsGrid.appendChild(frag);
  }

  // Update "showing" stat
  dom.statShowing.querySelector(".stat-value").textContent = releases.length;
}

// ============================================================
// Load releases (with current filters)
// ============================================================
async function loadReleases() {
  setLoading(true);
  try {
    const params = buildQueryParams();
    const res    = await fetch(`/api/releases?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    state.releases    = data.releases   || [];
    state.brands      = data.brands     || [];
    state.saleMethods = data.sale_methods || [];

    populateDropdowns();
    render(state.releases);

    dom.totalBadge.textContent = data.total ?? data.count ?? state.releases.length;
    if (data.last_updated) {
      dom.lastUpdated.textContent = "Updated " + timeAgo(data.last_updated);
    }
  } catch (err) {
    console.error("loadReleases error:", err);
    showToast("Failed to load releases – " + err.message, "error");
    dom.emptyState.classList.remove("hidden");
    dom.cardsGrid.classList.add("hidden");
  } finally {
    setLoading(false);
  }
}

// ============================================================
// Load stats
// ============================================================
async function loadStats() {
  try {
    const res  = await fetch("/api/stats");
    const data = await res.json();
    dom.statTotal.querySelector(".stat-value").textContent    = data.total    ?? "–";
    dom.statUpcoming.querySelector(".stat-value").textContent = data.upcoming_count ?? "–";
    dom.statGrail.querySelector(".stat-value").textContent    = data.grail_count    ?? "–";
  } catch (e) {
    console.error("loadStats error:", e);
  }
}

// ============================================================
// Build query string from current filter state
// ============================================================
function buildQueryParams() {
  const p = new URLSearchParams();

  const search = dom.searchInput.value.trim();
  if (search) p.set("search", search);

  const brand = dom.brandFilter.value;
  if (brand)  p.set("brand", brand);

  const low  = parseInt(dom.hypeLow.value, 10);
  const high = parseInt(dom.hypeHigh.value, 10);
  if (low  > 1) p.set("hype_min", low);
  if (high < 5) p.set("hype_max", high);

  const method = dom.methodFilter.value;
  if (method) p.set("sale_method", method);

  const sortRaw = dom.sortBy.value;
  if (sortRaw.endsWith("_desc")) {
    p.set("sort_by",    sortRaw.replace("_desc", ""));
    p.set("sort_order", "desc");
  } else {
    p.set("sort_by",    sortRaw);
    p.set("sort_order", "asc");
  }

  return p.toString();
}

// ============================================================
// Populate brand / method dropdowns (preserve selected value)
// ============================================================
function populateDropdowns() {
  const selectedBrand  = dom.brandFilter.value;
  const selectedMethod = dom.methodFilter.value;

  dom.brandFilter.innerHTML = `<option value="">All Brands</option>`;
  state.brands.forEach(b => {
    const opt = document.createElement("option");
    opt.value       = b;
    opt.textContent = b;
    if (b === selectedBrand) opt.selected = true;
    dom.brandFilter.appendChild(opt);
  });

  dom.methodFilter.innerHTML = `<option value="">All Methods</option>`;
  state.saleMethods.forEach(m => {
    const opt = document.createElement("option");
    opt.value       = m;
    opt.textContent = m;
    if (m === selectedMethod) opt.selected = true;
    dom.methodFilter.appendChild(opt);
  });
}

// ============================================================
// Refresh (trigger new scrape)
// ============================================================
async function doRefresh() {
  if (state.loading) return;
  dom.refreshBtn.disabled = true;
  dom.refreshBtn.textContent = "⟳ Scraping…";
  showToast("Scraping sneaker sites… this may take 15–30s", "info");

  try {
    const res  = await fetch("/api/refresh", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(`✓ ${data.count} releases loaded`, "success");
      await loadReleases();
      await loadStats();
    } else {
      showToast("Scrape error: " + (data.error || "Unknown"), "error");
    }
  } catch (err) {
    showToast("Network error: " + err.message, "error");
  } finally {
    dom.refreshBtn.disabled = false;
    dom.refreshBtn.textContent = "⟳ Refresh";
  }
}

// ============================================================
// Excel export
// ============================================================
function doExport() {
  const params = buildQueryParams();
  const url    = `/api/export/excel?${params}`;
  const a      = document.createElement("a");
  a.href       = url;
  a.download   = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast("📥 Downloading Excel…", "info");
}

// ============================================================
// Toast
// ============================================================
let toastTimer = null;
function showToast(msg, type = "info") {
  dom.toast.textContent = msg;
  dom.toast.className   = `toast toast--${type}`;
  dom.toast.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => dom.toast.classList.add("hidden"), 4000);
}

// ============================================================
// Loading state
// ============================================================
function setLoading(on) {
  state.loading = on;
  if (on) {
    dom.loader.classList.remove("hidden");
    dom.cardsGrid.classList.add("hidden");
    dom.emptyState.classList.add("hidden");
  } else {
    dom.loader.classList.add("hidden");
  }
}

// ============================================================
// Time ago helper
// ============================================================
function timeAgo(isoStr) {
  const diff = Math.floor((Date.now() - new Date(isoStr)) / 1000);
  if (diff < 60)   return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400)return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// ============================================================
// Debounce
// ============================================================
function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ============================================================
// Event listeners
// ============================================================
function attachListeners() {
  // Search
  dom.searchInput.addEventListener("input",  debounce(loadReleases, 300));

  // Filters
  dom.brandFilter.addEventListener("change", loadReleases);
  dom.methodFilter.addEventListener("change", loadReleases);
  dom.sortBy.addEventListener("change",      loadReleases);

  dom.hypeLow.addEventListener("change", () => {
    // Ensure low <= high
    if (parseInt(dom.hypeLow.value) > parseInt(dom.hypeHigh.value)) {
      dom.hypeHigh.value = dom.hypeLow.value;
    }
    loadReleases();
  });
  dom.hypeHigh.addEventListener("change", () => {
    if (parseInt(dom.hypeHigh.value) < parseInt(dom.hypeLow.value)) {
      dom.hypeLow.value = dom.hypeHigh.value;
    }
    loadReleases();
  });

  // Clear filters
  dom.clearFilters.addEventListener("click", () => {
    dom.searchInput.value   = "";
    dom.brandFilter.value   = "";
    dom.methodFilter.value  = "";
    dom.hypeLow.value       = "1";
    dom.hypeHigh.value      = "5";
    dom.sortBy.value        = "release_date";
    loadReleases();
  });

  // Refresh
  dom.refreshBtn.addEventListener("click", doRefresh);

  // Export
  dom.exportBtn.addEventListener("click", doExport);

  // Legend
  dom.legendBtn.addEventListener("click",   () => dom.legendModal.classList.remove("hidden"));
  dom.legendClose.addEventListener("click", () => dom.legendModal.classList.add("hidden"));
  dom.legendModal.addEventListener("click", e => {
    if (e.target === dom.legendModal) dom.legendModal.classList.add("hidden");
  });

  // Keyboard: Esc closes modal
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") dom.legendModal.classList.add("hidden");
  });
}

// ============================================================
// Init
// ============================================================
(async function init() {
  attachListeners();
  await loadReleases();
  await loadStats();
})();
