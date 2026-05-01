// Page views — Summary, Releases, Calendar, HypeWatch, Brands, Watchlist, Detail modal
const { useState: uS, useEffect: uE, useMemo: uM, useRef: uR } = React;

// ── Score breakdown helper ───────────────────────────────────
function scoreBreakdown(r) {
  const hasMv = r.estimated_market_value != null;
  const resell = hasMv ? Math.min(10, Math.round((r.estimated_market_value / r.retail_price) * 3)) : null;
  const brandScores = { Jordan: 9, Yeezy: 9, Nike: 7, "New Balance": 6, Adidas: 5, Converse: 5, HOKA: 3, On: 3 };
  const brand = brandScores[r.brand] ?? 5;
  const silhouettes = { "AJ1": 9, "AJ4": 9, "Dunk": 9, "Yeezy 350": 9, "990": 9, "AJ12": 6, "Vapormax": 6, "Blazer": 6 };
  let sil = 3;
  Object.keys(silhouettes).forEach(k => { if (r.name.includes(k) || r.name.includes(k.replace("AJ", "Air Jordan "))) sil = silhouettes[k]; });
  const collabs = ["Travis Scott", "Off-White", "Virgil Abloh", "Supreme", "sacai", "Bad Bunny", "Fragment", "Aimé Leon Dore", "Swarovski"];
  const collab = collabs.some(c => r.name.includes(c)) ? 10 : 3;
  return { resell, brand, sil, collab, hasMv };
}

// ────────────────────────────────────────────────────────────
//   SUMMARY
// ────────────────────────────────────────────────────────────
function SummaryView({ releases, onOpen, watchlist, toggleWatch, navigate }) {
  const total = releases.length;
  const ext = releases.filter(r => r.hype_level === "EXTREME").length;
  const hi  = releases.filter(r => r.hype_level === "HIGH").length;
  const wk  = releases.filter(r => r.days_until_release <= 7).length;
  const month = releases.filter(r => r.days_until_release >= 8 && r.days_until_release <= 30).length;
  const counts = useMemo(() => {
    const c = { EXTREME: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    releases.forEach(r => c[r.hype_level]++);
    return c;
  }, [releases]);
  const topHype = useMemo(() =>
    [...releases].sort((a, b) => b.hype_score - a.hype_score || a.days_until_release - b.days_until_release).slice(0, 6),
  [releases]);
  const droppingToday = useMemo(() => releases.filter(r => r.days_until_release === 0), [releases]);

  return (
    <div className="page" data-screen-label="01 Summary">
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Sneaker Tracker · 90-day window</div>
          <h1 className="page-title">
            <span style={{ fontWeight: 500, fontFeatureSettings: "'tnum'" }}>{total}</span> upcoming releases<br />
            <span style={{ color: "var(--muted)", fontWeight: 400, fontSize: 26 }}>tracked across {Object.keys(window.BRAND_META).length} brands</span>
          </h1>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <a className="btn ghost" href={window.EXCEL_PATH} download><Icons.External size={14} /> Excel report</a>
          <button className="btn ghost" onClick={() => navigate("calendar")}><Icons.Calendar size={14} /> Calendar</button>
          <button className="btn primary" onClick={() => navigate("hype")}><Icons.Flame size={14} /> Hype Watch</button>
        </div>
      </div>

      <div className="stat-ribbon">
        <div className="stat-cell">
          <div className="stat-cell-label">Total</div>
          <div className="stat-cell-value accent">{total}</div>
          <div className="stat-cell-sub">next 90 days <span className="delta up">+4 this week</span></div>
          <div className="stat-spark"><Sparkline values={[3,5,4,7,6,9,8,11]} /></div>
        </div>
        <div className="stat-cell">
          <div className="stat-cell-label">Extreme</div>
          <div className="stat-cell-value extreme">{ext}</div>
          <div className="stat-cell-sub">must-cop releases</div>
        </div>
        <div className="stat-cell">
          <div className="stat-cell-label">High</div>
          <div className="stat-cell-value high">{hi}</div>
          <div className="stat-cell-sub">expected to sell out</div>
        </div>
        <div className="stat-cell">
          <div className="stat-cell-label">Within 7 days</div>
          <div className="stat-cell-value urgent">{wk}</div>
          <div className="stat-cell-sub">{month} more in 30</div>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <div className="section-title">
            Top hype <span className="section-title-num">— scored 7+</span>
          </div>
          <button className="section-action" onClick={() => navigate("hype")}>View all <Icons.ChevR size={12} /></button>
        </div>
        <div className="grid-3">
          {topHype.map(r => <ReleaseCard key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="section-head" style={{ marginBottom: 14 }}>
            <div className="section-title">Hype distribution</div>
          </div>
          <HypeDonut counts={counts} />
        </div>
        <div className="card">
          <div className="section-head" style={{ marginBottom: 14 }}>
            <div className="section-title">Releases by brand</div>
          </div>
          <BrandBars releases={releases} />
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <div className="section-title">Today's releases <span className="section-title-num">— {droppingToday.length} {droppingToday.length === 1 ? "drop" : "drops"}</span></div>
          <button className="section-action" onClick={() => navigate("releases")}>All releases <Icons.ChevR size={12} /></button>
        </div>
        {droppingToday.length === 0 ? (
          <div className="empty">
            <div className="e-title">No drops today</div>
            <div className="muted-text">Check the calendar for what's next.</div>
          </div>
        ) : (
          <ReleaseList rows={droppingToday} view="list" onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />
        )}
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   RELEASES — filterable list
// ────────────────────────────────────────────────────────────
function ReleasesView({ releases, onOpen, watchlist, toggleWatch, view, setView, search }) {
  const [brand, setBrand] = uS("");
  const [hype, setHype] = uS("");
  const [days, setDays] = uS("");
  const [sort, setSort] = uS("days_until_release");

  const brands = useMemo(() => [...new Set(releases.map(r => r.brand))].sort(), [releases]);

  const rows = useMemo(() => {
    let l = releases.filter(r => {
      if (brand && r.brand !== brand) return false;
      if (hype && r.hype_level !== hype) return false;
      if (days && r.days_until_release > parseInt(days)) return false;
      if (search && !r.name.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
    const dir = sort === "hype_score" || sort === "retail_price" ? -1 : 1;
    l.sort((a, b) => {
      const av = a[sort] ?? 0, bv = b[sort] ?? 0;
      return typeof av === "string" ? av.localeCompare(bv) * dir : (av - bv) * dir;
    });
    return l;
  }, [releases, brand, hype, days, sort, search]);

  return (
    <div className="page" data-screen-label="02 Releases">
      <div className="page-header">
        <div>
          <div className="page-eyebrow">All releases</div>
          <h1 className="page-title">Release calendar</h1>
          <div className="page-sub">Every confirmed drop in the next 90 days, with hype, retail, and resell intel.</div>
        </div>
      </div>

      <div className="filters">
        <span className="mono" style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".08em", padding: "0 8px" }}>Hype</span>
        {["", "EXTREME", "HIGH", "MEDIUM", "LOW"].map(h => (
          <button key={h} className={`filter-chip ${hype === h ? "active" : ""}`} onClick={() => setHype(h)}>
            {h || "All"}
            {h && <span className="ch-count">{releases.filter(r => r.hype_level === h).length}</span>}
          </button>
        ))}
        <span className="filter-divider"></span>
        <select className="filter-chip" value={brand} onChange={e => setBrand(e.target.value)} style={{ padding: "6px 10px" }}>
          <option value="">All brands</option>
          {brands.map(b => <option key={b} value={b}>{b}</option>)}
        </select>
        <select className="filter-chip" value={days} onChange={e => setDays(e.target.value)} style={{ padding: "6px 10px" }}>
          <option value="">Any time</option>
          <option value="7">≤ 7 days</option>
          <option value="14">≤ 14 days</option>
          <option value="30">≤ 30 days</option>
        </select>
        <select className="filter-chip" value={sort} onChange={e => setSort(e.target.value)} style={{ padding: "6px 10px" }}>
          <option value="days_until_release">Sort: Date ↑</option>
          <option value="hype_score">Sort: Hype ↓</option>
          <option value="retail_price">Sort: Price ↓</option>
          <option value="brand">Sort: Brand</option>
        </select>
        <div className="view-toggle">
          {[
            { k: "grid", icon: Icons.Grid },
            { k: "list", icon: Icons.List },
            { k: "feed", icon: Icons.Feed },
          ].map(v => (
            <button key={v.k} className={view === v.k ? "active" : ""} onClick={() => setView(v.k)}>
              <v.icon size={12} /> {v.k}
            </button>
          ))}
        </div>
      </div>

      <div className="mono" style={{ fontSize: 11, color: "var(--muted)", padding: "0 4px" }}>
        {rows.length} {rows.length === 1 ? "release" : "releases"} · sorted by {sort.replace(/_/g, " ")}
      </div>

      <ReleaseList rows={rows} view={view} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   CALENDAR
// ────────────────────────────────────────────────────────────
function CalendarView({ releases, onOpen, watchlist, toggleWatch }) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const [m, setM] = uS(today.getMonth());
  const [y, setY] = uS(today.getFullYear());
  const [selected, setSelected] = uS(null);

  const first = new Date(y, m, 1);
  // Monday-first week: shift so Mon=0…Sun=6
  const startDow = (first.getDay() + 6) % 7;
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startDow; i++) {
    const d = new Date(y, m, -startDow + i + 1);
    cells.push({ date: d, otherMonth: true });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ date: new Date(y, m, d), otherMonth: false });
  }
  while (cells.length % 7 !== 0 || cells.length < 42) {
    const last = cells[cells.length - 1].date;
    const next = new Date(last); next.setDate(next.getDate() + 1);
    cells.push({ date: next, otherMonth: next.getMonth() !== m });
    if (cells.length >= 42) break;
  }

  function relForDate(d) {
    const iso = d.toISOString().slice(0, 10);
    return releases.filter(r => r.release_date === iso);
  }
  const monthName = first.toLocaleDateString("en-US", { month: "long" });

  const selectedReleases = selected ? relForDate(selected) : [];

  return (
    <div className="page" data-screen-label="03 Calendar">
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Drop calendar</div>
          <h1 className="page-title"><span className="serif">{monthName}</span> {y}</h1>
        </div>
        <div className="cal-nav">
          <button className="icon-btn" onClick={() => { const nd = new Date(y, m - 1, 1); setY(nd.getFullYear()); setM(nd.getMonth()); }}><Icons.ChevL size={14} /></button>
          <button className="btn ghost" onClick={() => { setY(today.getFullYear()); setM(today.getMonth()); }}>Today</button>
          <button className="icon-btn" onClick={() => { const nd = new Date(y, m + 1, 1); setY(nd.getFullYear()); setM(nd.getMonth()); }}><Icons.ChevR size={14} /></button>
        </div>
      </div>

      <div className="calendar">
        <div className="cal-grid-head">
          {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map(d => <div key={d}>{d}</div>)}
        </div>
        <div className="cal-grid">
          {cells.map((c, i) => {
            const rel = relForDate(c.date);
            const isToday = c.date.getTime() === today.getTime();
            return (
              <div key={i}
                className={`cal-day ${c.otherMonth ? "other-month" : ""} ${isToday ? "today" : ""}`}
                onClick={() => rel.length && setSelected(c.date)}
                style={{ cursor: rel.length ? "pointer" : "default" }}>
                <div className="cal-num">{c.date.getDate()}</div>
                {rel.slice(0, 4).map(r => (
                  <div key={r.id} className={`cal-pill ${r.hype_level}`} title={r.name}>{r.name}</div>
                ))}
                {rel.length > 4 && <div className="cal-overflow">+{rel.length - 4} more</div>}
              </div>
            );
          })}
        </div>
      </div>

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 1080, width: "calc(100vw - 80px)" }}>
            <div style={{ padding: "24px 28px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div className="page-eyebrow" style={{ marginBottom: 4 }}>{selected.toLocaleDateString("en-US", { weekday: "long" })}</div>
                <div className="serif" style={{ fontSize: 28, lineHeight: 1, letterSpacing: "-0.02em" }}>
                  {selected.toLocaleDateString("en-US", { month: "long", day: "numeric" })}
                </div>
              </div>
              <button className="icon-btn" onClick={() => setSelected(null)}><Icons.Close size={14} /></button>
            </div>
            <div style={{ padding: 0 }}>
              {selectedReleases.map(r => <ReleaseRow key={r.id} r={r} onOpen={(rr) => { setSelected(null); onOpen(rr); }} watchlist={watchlist} toggleWatch={toggleWatch} />)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   HYPE WATCH
// ────────────────────────────────────────────────────────────
function HypeWatchView({ releases, onOpen, watchlist, toggleWatch }) {
  const hype = useMemo(() =>
    releases.filter(r => r.hype_level === "HIGH" || r.hype_level === "EXTREME")
            .sort((a, b) => b.hype_score - a.hype_score || a.days_until_release - b.days_until_release),
  [releases]);
  const ext = hype.filter(r => r.hype_level === "EXTREME");

  return (
    <div className="page" data-screen-label="04 Hype Watch">
      <div className="hype-banner">
        <div style={{ position: "relative", zIndex: 1 }}>
          <div className="hype-banner-eyebrow">◆ Hype Watch</div>
          <div className="hype-banner-title">High-demand drops, ranked by score and proximity.</div>
          <div className="page-sub" style={{ marginTop: 14 }}>Only releases scoring 7 or above. Resell premium estimates from secondary market data.</div>
        </div>
        <div className="hype-banner-stats">
          <div className="hype-banner-stat">
            <div className="v">{ext.length}</div>
            <div className="l">Extreme</div>
          </div>
          <div className="hype-banner-stat">
            <div className="v">{hype.length}</div>
            <div className="l">Total</div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <div className="section-title">Extreme tier <span className="section-title-num">— {ext.length} drops</span></div>
        </div>
        <div className="grid-3">
          {ext.map(r => <ReleaseCard key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <div className="section-title">All hype releases</div>
        </div>
        <ReleaseList rows={hype} view="list" onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   BRANDS
// ────────────────────────────────────────────────────────────
function BrandsView({ releases, onOpen, watchlist, toggleWatch }) {
  const [active, setActive] = uS(null);

  const byBrand = useMemo(() => {
    const m = {};
    releases.forEach(r => { (m[r.brand] = m[r.brand] || []).push(r); });
    return m;
  }, [releases]);

  if (active && byBrand[active]) {
    const list = byBrand[active];
    const ext = list.filter(r => r.hype_level === "EXTREME").length;
    const hi = list.filter(r => r.hype_level === "HIGH").length;
    const meta = window.BRAND_META[active] || {};
    return (
      <div className="page" data-screen-label="05 Brand">
        <button className="section-action" onClick={() => setActive(null)} style={{ alignSelf: "flex-start" }}>
          <Icons.ChevL size={12} /> All brands
        </button>
        <div className="page-header">
          <div>
            <div className="page-eyebrow">Brand · {meta.tagline || ""} · est. {meta.founded || "—"}</div>
            <h1 className="page-title">
              <span className="serif">{active}</span>
            </h1>
            <div className="page-sub">{list.length} upcoming releases · {ext} Extreme · {hi} High</div>
          </div>
        </div>
        <BrandBars releases={list} max={20} />
        <div className="grid-3">
          {list.map(r => <ReleaseCard key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
        </div>
      </div>
    );
  }

  return (
    <div className="page" data-screen-label="05 Brands">
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Brands</div>
          <h1 className="page-title">{Object.keys(byBrand).length} brands tracked</h1>
        </div>
      </div>
      <div className="grid-3">
        {Object.entries(byBrand)
          .sort((a, b) => b[1].length - a[1].length)
          .map(([b, list]) => {
            const ext = list.filter(r => r.hype_level === "EXTREME").length;
            const hi  = list.filter(r => r.hype_level === "HIGH").length;
            const meta = window.BRAND_META[b] || {};
            const hue = meta.hue ?? 200;
            return (
              <div key={b} className="brand-card" onClick={() => setActive(b)}>
                <div style={{
                  position: "absolute", inset: 0,
                  background: `radial-gradient(circle at 100% 0%, oklch(0.7 0.15 ${hue} / 0.18), transparent 60%)`,
                  pointerEvents: "none",
                }} />
                <div style={{ position: "relative", zIndex: 1 }}>
                  <div className="brand-card-tag">{meta.tagline || "—"}</div>
                  <div className="brand-card-name">{b}</div>
                </div>
                <div className="brand-card-stats">
                  <div className="brand-card-stat"><div className="v">{list.length}</div><div className="l">Drops</div></div>
                  <div className="brand-card-stat"><div className="v">{ext}</div><div className="l">Extreme</div></div>
                  <div className="brand-card-stat"><div className="v">{hi}</div><div className="l">High</div></div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   WATCHLIST
// ────────────────────────────────────────────────────────────
function WatchlistView({ releases, onOpen, watchlist, toggleWatch }) {
  const list = releases.filter(r => watchlist.has(r.id))
                       .sort((a, b) => a.days_until_release - b.days_until_release);
  const [view, setView] = uS("grid");
  return (
    <div className="page" data-screen-label="06 Watchlist">
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Saved · {list.length}</div>
          <h1 className="page-title"><span className="serif">Your</span> watchlist</h1>
          <div className="page-sub">Personal queue. Get a drop reminder 24h before each release date.</div>
        </div>
        {list.length > 0 && (
          <div className="view-toggle">
            {[
              { k: "grid", icon: Icons.Grid },
              { k: "list", icon: Icons.List },
            ].map(({ k, icon: I }) => (
              <button key={k} className={"vt-btn" + (view === k ? " on" : "")} onClick={() => setView(k)} title={k}>
                <I size={14} />
              </button>
            ))}
          </div>
        )}
      </div>
      {list.length === 0 ? (
        <div className="empty">
          <div className="e-title">Nothing saved yet</div>
          <div className="muted-text">Tap the bookmark on any release to add it here.</div>
        </div>
      ) : (
        <ReleaseList rows={list} view={view} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────
//   DETAIL MODAL
// ────────────────────────────────────────────────────────────
function DetailModal({ release: r, onClose, watchlist, toggleWatch }) {
  if (!r) return null;
  const sb = scoreBreakdown(r);
  const premium = r.estimated_market_value
    ? Math.round((r.estimated_market_value / r.retail_price - 1) * 100)
    : null;

  uE(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{ position: "relative" }}>
        <button className="icon-btn modal-close" onClick={onClose}><Icons.Close size={14} /></button>
        <div className="modal-hero">
          <div className={"modal-img" + (r.image_url ? " has-img" : "")}>
            {r.image_url && <img src={r.image_url} alt={r.name} onError={(e) => e.currentTarget.parentElement.classList.remove("has-img")} />}
            {r.style_code && <span className="modal-img-label">{r.style_code}</span>}
          </div>
          <div className="modal-info">
            <div className="modal-meta-row">
              <BrandChip brand={r.brand} />
              <DaysPill days={r.days_until_release} date={r.release_date} />
              <HypeBadge level={r.hype_level} score={r.hype_score} />
            </div>
            <div className="modal-name">{r.name}</div>
            {r.colorway && <div className="release-colorway">{r.colorway}</div>}
            <div className="modal-pricing">
              <div className="price-box">
                <div className="price-label">Retail</div>
                <div className="price-val"><span className="currency">$</span>{r.retail_price?.toFixed(0) ?? "TBD"}</div>
                <div className="price-delta">{r.sale_method}</div>
              </div>
              <div className="price-box">
                <div className="price-label">Est. market value</div>
                <div className="price-val"><span className="currency">$</span>{r.estimated_market_value ?? "—"}</div>
                {premium != null && <div className="price-delta up">+{premium}% premium</div>}
              </div>
            </div>
            <div className="modal-actions">
              <button
                className={`btn ${watchlist.has(r.id) ? "" : "primary"}`}
                onClick={() => toggleWatch(r.id)}
              >
                <Icons.Bookmark size={14} fill={watchlist.has(r.id) ? "currentColor" : "none"} />
                {watchlist.has(r.id) ? "Saved · we'll remind you 24h before" : "Save to watchlist"}
              </button>
              <a className="btn ghost" href={r.source_url} target="_blank" rel="noopener noreferrer">
                <Icons.External size={14} /> View on {r.source}
              </a>
            </div>
          </div>
        </div>

        <div className="modal-body">
          <div>
            <div className="page-eyebrow" style={{ marginBottom: 12 }}>Release details</div>
            <dl className="fact-list">
              <dt>Release date</dt><dd>{fmtFullDate(r.release_date)}</dd>
              <dt>Style code</dt><dd className="mono">{r.style_code || "—"}</dd>
              <dt>Colorway</dt><dd>{r.colorway || "—"}</dd>
              <dt>Sale method</dt><dd>{r.sale_method || "—"}</dd>
              <dt>Source</dt><dd><SourceLink r={r} /></dd>
            </dl>
          </div>
          <div>
            <div className="page-eyebrow" style={{ marginBottom: 12 }}>Hype score · {r.hype_score}/10</div>
            <div className="score-breakdown">
              {[
                { l: "Resell prem.", v: sb.resell, w: sb.hasMv ? 50 : 0 },
                { l: "Brand",        v: sb.brand,  w: sb.hasMv ? 20 : 35 },
                { l: "Silhouette",   v: sb.sil,    w: sb.hasMv ? 20 : 45 },
                { l: "Collaborator", v: sb.collab, w: sb.hasMv ? 10 : 20 },
              ].filter(s => s.w > 0).map(s => (
                <div key={s.l} className="score-row">
                  <div className="label">{s.l} <span style={{ opacity: 0.6 }}>{s.w}%</span></div>
                  <div className="score-bar">
                    <div className="score-bar-fill" style={{ width: `${(s.v ?? 0) * 10}%` }} />
                  </div>
                  <div className="val">{s.v ?? "—"}</div>
                </div>
              ))}
            </div>
            <div className="muted-text" style={{ fontSize: 11.5, marginTop: 10, fontFamily: "var(--font-mono)" }}>
              {sb.hasMv ? "Weighted with resell market data." : "No market data — weights redistributed."}
            </div>
          </div>
        </div>

        <div className="buy-section">
          <div className="page-eyebrow" style={{ marginBottom: 14 }}>Buy at</div>
          <div className="buy-grid">
            {window.buyLinks(r).map(link => (
              <a
                key={link.name}
                className={"buy-link" + (link.primary ? " primary" : "") + (link.resell ? " resell" : "")}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="buy-link-row">
                  <span className="buy-link-name">{link.name}</span>
                  <Icons.External size={11} />
                </div>
                <div className="buy-link-tag">{link.tag}</div>
              </a>
            ))}
          </div>
          <div className="muted-text" style={{ fontSize: 11, marginTop: 12, fontFamily: "var(--font-mono)" }}>
            Links open a search on each retailer for {r.style_code}. Availability and timing varies by region.
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, {
  SummaryView, ReleasesView, CalendarView, HypeWatchView, BrandsView, WatchlistView, DetailModal,
});
