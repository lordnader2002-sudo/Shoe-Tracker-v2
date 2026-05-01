// Loads live release data from reports/releases.json (refreshed daily by the
// scraper pipeline). Falls back to docs/data/releases.json in case the site
// is served from the docs/ directory.

(function () {
  // Prefer docs/data/releases.json — that's where the daily scraper writes
  // the canonical refresh. reports/ exists as a legacy fallback.
  const FETCH_PATHS = ["docs/data/releases.json", "data/releases.json", "reports/releases.json"];

  window.RELEASES = null;
  window.GENERATED_AT = "Loading…";

  window.loadReleases = async function () {
    let lastErr;
    for (const p of FETCH_PATHS) {
      try {
        const resp = await fetch(p, { cache: "no-cache" });
        if (!resp.ok) { lastErr = new Error(`HTTP ${resp.status} on ${p}`); continue; }
        const json = await resp.json();
        const releases = (json.releases || []).map(normalize);
        window.RELEASES = releases;
        window.GENERATED_AT = formatGeneratedAt(json.generated_at);
        // Excel sits next to the JSON.
        window.EXCEL_PATH = p.replace(/releases\.json$/, "sneaker_releases.xlsx");
        return { releases, generated_at: window.GENERATED_AT };
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("releases.json not found");
  };

  function normalize(r) {
    const isNA = (v) => v == null || v === "" || v === "N/A";
    return {
      ...r,
      id: r.id || `rel-${slug(r.name)}-${r.release_date || ""}`,
      colorway:   isNA(r.colorway)   ? null : r.colorway,
      style_code: isNA(r.style_code) ? null : r.style_code,
      image_url:  isNA(r.image_url)  ? null : r.image_url,
      retail_price:           r.retail_price ?? null,
      estimated_market_value: r.estimated_market_value ?? null,
    };
  }

  function slug(s) {
    return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 60);
  }

  function formatGeneratedAt(iso) {
    // "Friday, May 1, 2026 at 0216 ET" — anchored to America/New_York
    // since the pipeline refreshes daily at 1:00 AM EST.
    const fmt = (d) => {
      const parts = new Intl.DateTimeFormat("en-US", {
        weekday: "long", month: "long", day: "numeric", year: "numeric",
        hour: "2-digit", minute: "2-digit", hour12: false,
        timeZone: "America/New_York",
      }).formatToParts(d);
      const get = (t) => parts.find((p) => p.type === t)?.value || "";
      let hh = get("hour"); if (hh === "24") hh = "00";
      return `${get("weekday")}, ${get("month")} ${get("day")}, ${get("year")} at ${hh}${get("minute")} ET`;
    };
    if (!iso) return fmt(new Date());
    const d = new Date(iso);
    return isNaN(d.getTime()) ? iso : fmt(d);
  }

  // Buy-at retailer logic. Sneaker drops sell through different channels; we
  // return real retailer search URLs scoped to the shoe's name + style code.
  window.buyLinks = function (r) {
    const queryStr = [r.name, r.style_code].filter(Boolean).join(" ");
    const q = encodeURIComponent(queryStr);
    const links = [];
    const method = r.sale_method;
    const brand = r.brand;

    if (method === "SNKRS App") {
      links.push({ name: "Nike SNKRS", tag: "Primary · raffle entry", url: `https://www.nike.com/launch?s=${q}`, primary: true });
    } else if (method === "Confirmed App") {
      links.push({ name: "adidas Confirmed", tag: "Primary · raffle entry", url: `https://www.adidas.com/us/confirmed?q=${q}`, primary: true });
    } else if (brand === "Nike" || brand === "Jordan") {
      links.push({ name: "Nike.com", tag: "Brand · launch page", url: `https://www.nike.com/w?q=${q}`, primary: true });
    } else if (brand === "Adidas") {
      links.push({ name: "adidas.com", tag: "Brand · launch page", url: `https://www.adidas.com/us/search?q=${q}`, primary: true });
    } else if (brand === "New Balance") {
      links.push({ name: "newbalance.com", tag: "Brand · launch page", url: `https://www.newbalance.com/search?q=${q}`, primary: true });
    } else if (brand === "Converse") {
      links.push({ name: "converse.com", tag: "Brand · launch page", url: `https://www.converse.com/shop/search?q=${q}`, primary: true });
    } else if (brand === "Puma") {
      links.push({ name: "puma.com", tag: "Brand · launch page", url: `https://us.puma.com/us/en/search?q=${q}`, primary: true });
    } else if (brand === "Reebok") {
      links.push({ name: "reebok.com", tag: "Brand · launch page", url: `https://www.reebok.com/search?q=${q}`, primary: true });
    } else if (brand === "Vans") {
      links.push({ name: "vans.com", tag: "Brand · launch page", url: `https://www.vans.com/en-us/search?q=${q}`, primary: true });
    }

    if (method === "Raffle/Dropship") {
      links.push({ name: "END.", tag: "Raffle entry", url: `https://www.endclothing.com/us/search?search=${q}` });
      links.push({ name: "Sneakersnstuff", tag: "Raffle entry", url: `https://www.sneakersnstuff.com/en/search?q=${q}` });
    }
    links.push({ name: "Foot Locker", tag: "Retailer", url: `https://www.footlocker.com/search?query=${q}` });
    links.push({ name: "Finish Line", tag: "Retailer", url: `https://www.finishline.com/store/search/searchResults.jsp?Ntt=${q}` });
    links.push({ name: "StockX", tag: "Resell market", url: `https://stockx.com/search?s=${q}`, resell: true });
    links.push({ name: "GOAT",   tag: "Resell market", url: `https://www.goat.com/search?query=${q}`, resell: true });

    return links;
  };

  // Brand metadata for brand pages
  window.BRAND_META = {
    "Nike":        { tagline: "Beaverton, OR",      hue: 210, founded: 1964 },
    "Jordan":      { tagline: "Jumpman",            hue: 0,   founded: 1984 },
    "Adidas":      { tagline: "Herzogenaurach",     hue: 30,  founded: 1949 },
    "New Balance": { tagline: "Boston, MA",         hue: 250, founded: 1906 },
    "Yeezy":       { tagline: "Calabasas",          hue: 50,  founded: 2015 },
    "Converse":    { tagline: "All-Star",           hue: 0,   founded: 1908 },
    "HOKA":        { tagline: "Trail / Road",       hue: 160, founded: 2009 },
    "On":          { tagline: "Zürich",             hue: 180, founded: 2010 },
    "Puma":        { tagline: "Herzogenaurach",     hue: 130, founded: 1948 },
    "Reebok":      { tagline: "Boston, MA",         hue: 280, founded: 1958 },
    "Vans":        { tagline: "Costa Mesa",         hue: 350, founded: 1966 },
  };

  // Default Excel path; overwritten once we know which JSON path resolved.
  window.EXCEL_PATH = "reports/sneaker_releases.xlsx";
})();
