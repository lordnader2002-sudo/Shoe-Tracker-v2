// Shared components & helpers
const { useState, useEffect, useMemo, useRef, useCallback } = React;

// ── Icons (inline SVG, lucide-style) ─────────────────────────
const Icon = ({ d, size = 16, fill = "none", stroke = "currentColor", strokeWidth = 1.75, children }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={stroke}
       strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    {children || <path d={d} />}
  </svg>
);

const Icons = {
  Search:    (p) => <Icon {...p}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.35-4.35" /></Icon>,
  Heart:     (p) => <Icon {...p}><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" /></Icon>,
  Calendar:  (p) => <Icon {...p}><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></Icon>,
  Layers:    (p) => <Icon {...p}><path d="m12.83 2.18 8.4 4.2a1 1 0 0 1 0 1.79L12.83 12.4a2 2 0 0 1-1.66 0l-8.4-4.2a1 1 0 0 1 0-1.79l8.4-4.2a2 2 0 0 1 1.66 0z" /><path d="M2 17l8.79 4.4a2 2 0 0 0 1.66 0L22 17M2 12l8.79 4.4a2 2 0 0 0 1.66 0L22 12" /></Icon>,
  Flame:     (p) => <Icon {...p}><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" /></Icon>,
  Grid:      (p) => <Icon {...p}><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></Icon>,
  List:      (p) => <Icon {...p}><line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" /><line x1="8" y1="18" x2="21" y2="18" /><line x1="3" y1="6" x2="3.01" y2="6" /><line x1="3" y1="12" x2="3.01" y2="12" /><line x1="3" y1="18" x2="3.01" y2="18" /></Icon>,
  Feed:      (p) => <Icon {...p}><rect x="3" y="3" width="18" height="6" rx="1" /><rect x="3" y="13" width="18" height="8" rx="1" /></Icon>,
  ChevL:     (p) => <Icon {...p}><polyline points="15 18 9 12 15 6" /></Icon>,
  ChevR:     (p) => <Icon {...p}><polyline points="9 18 15 12 9 6" /></Icon>,
  Close:     (p) => <Icon {...p}><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></Icon>,
  Bell:      (p) => <Icon {...p}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></Icon>,
  Sparkles:  (p) => <Icon {...p}><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3z" /></Icon>,
  External:  (p) => <Icon {...p}><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" /></Icon>,
  Share:     (p) => <Icon {...p}><circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" /></Icon>,
  Tag:       (p) => <Icon {...p}><path d="M20.59 13.41 13.41 20.59a2 2 0 0 1-2.82 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" /></Icon>,
  Filter:    (p) => <Icon {...p}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" /></Icon>,
  ArrowUp:   (p) => <Icon {...p}><line x1="12" y1="19" x2="12" y2="5" /><polyline points="5 12 12 5 19 12" /></Icon>,
  ArrowDown: (p) => <Icon {...p}><line x1="12" y1="5" x2="12" y2="19" /><polyline points="19 12 12 19 5 12" /></Icon>,
  Check:     (p) => <Icon {...p}><polyline points="20 6 9 17 4 12" /></Icon>,
  Plus:      (p) => <Icon {...p}><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></Icon>,
  Bookmark:  (p) => <Icon {...p}><path d="m19 21-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" /></Icon>,
};

// ── Helpers ──────────────────────────────────────────────────
function fmtDate(iso, opts = { month: "short", day: "numeric" }) {
  if (!iso) return "—";
  return new Date(iso + "T00:00:00").toLocaleDateString("en-US", opts);
}
function fmtFullDate(iso) {
  return fmtDate(iso, { weekday: "long", month: "long", day: "numeric", year: "numeric" });
}
function daysLabel(n) {
  if (n === 0) return "Today";
  if (n === 1) return "Tomorrow";
  if (n < 0) return `${-n}d ago`;
  if (n < 7) return `In ${n} days`;
  if (n < 14) return `Next week`;
  if (n < 30) return `In ${Math.round(n / 7)}w`;
  return `In ${Math.round(n / 30)}mo`;
}
function daysClass(n) {
  if (n === 0) return "today";
  if (n <= 7) return "urgent";
  if (n <= 14) return "upcoming";
  return "";
}
function brandInitials(brand) {
  if (!brand) return "?";
  if (brand === "New Balance") return "NB";
  return brand.slice(0, 2).toUpperCase();
}
function brandHue(brand) {
  return (window.BRAND_META && window.BRAND_META[brand]?.hue) ?? 200;
}

// ── Hype badge ───────────────────────────────────────────────
function HypeBadge({ level, score }) {
  return (
    <span className={`hype-badge ${level}`}>
      <span className="hb-dot"></span>
      {level}
      {score != null && <span style={{ opacity: 0.7, marginLeft: 4 }}>{score}</span>}
    </span>
  );
}

// ── Days pill ────────────────────────────────────────────────
function DaysPill({ days, date }) {
  const cls = daysClass(days);
  return (
    <span className={`days-pill ${cls}`} title={date}>
      {daysLabel(days)}
    </span>
  );
}

// ── Brand chip ───────────────────────────────────────────────
function BrandChip({ brand }) {
  const hue = brandHue(brand);
  return (
    <span className="brand-chip">
      <span className="brand-chip-mark"
            style={{ background: `oklch(0.75 0.16 ${hue})`, color: "oklch(0.18 0.012 250)" }}>
        {brandInitials(brand).slice(0, 1)}
      </span>
      {brand}
    </span>
  );
}

// ── Watchlist heart ──────────────────────────────────────────
function WatchBtn({ id, watchlist, toggleWatch, size = 14 }) {
  const [pulsing, setPulsing] = useState(false);
  const isOn = watchlist.has(id);
  const onClick = (e) => {
    e.stopPropagation();
    toggleWatch(id);
    setPulsing(true);
    setTimeout(() => setPulsing(false), 400);
  };
  return (
    <button
      className={`watch-btn ${isOn ? "active" : ""} ${pulsing ? "pulsing" : ""}`}
      onClick={onClick}
      title={isOn ? "Remove from watchlist" : "Add to watchlist"}
    >
      <Icons.Bookmark size={size} fill={isOn ? "currentColor" : "none"} />
    </button>
  );
}

// ── External source link ─────────────────────────────────────
function SourceLink({ r, compact }) {
  if (!r.source_url) return null;
  return (
    <a
      className={"source-link" + (compact ? " compact" : "")}
      href={r.source_url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
      title={`View on ${r.source}`}
    >
      <Icons.External size={11} />
      <span>{compact ? "Source" : r.source}</span>
    </a>
  );
}

// ── Sparkline ────────────────────────────────────────────────
function Sparkline({ values, w = 64, h = 22 }) {
  const max = Math.max(...values, 1);
  const min = Math.min(...values);
  const range = max - min || 1;
  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return (
    <svg className="spark" width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <polyline points={points.join(" ")} fill="none" stroke="var(--accent)" strokeWidth="1.5" />
    </svg>
  );
}

// ── Release card ─────────────────────────────────────────────
function ReleaseCard({ r, onOpen, watchlist, toggleWatch }) {
  return (
    <div className="release-card" onClick={() => onOpen(r)}>
      <div className={"release-img" + (r.image_url ? " has-img" : "")}>
        {r.image_url && <img src={r.image_url} alt={r.name} loading="lazy" onError={(e) => e.currentTarget.parentElement.classList.remove("has-img")} />}
        {r.style_code && <span className="release-img-label">{r.style_code}</span>}
        <WatchBtn id={r.id} watchlist={watchlist} toggleWatch={toggleWatch} />
      </div>
      <div className="release-body">
        <div className="release-meta">
          <BrandChip brand={r.brand} />
          <span className="dot-sep"></span>
          <span>{fmtDate(r.release_date)}</span>
          <SourceLink r={r} compact />
        </div>
        <div className="release-name">{r.name}</div>
        {r.colorway && <div className="release-colorway">{r.colorway}</div>}
        <div className="release-foot">
          <div>
            <div className="release-price">
              <span className="currency">$</span>{r.retail_price?.toFixed(0) ?? "TBD"}
            </div>
            {r.estimated_market_value && (
              <div className="release-mv">
                MV <span className="up">${r.estimated_market_value} · +{Math.round((r.estimated_market_value/r.retail_price - 1) * 100)}%</span>
              </div>
            )}
          </div>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <DaysPill days={r.days_until_release} date={r.release_date} />
            <HypeBadge level={r.hype_level} score={r.hype_score} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Release list row ─────────────────────────────────────────
function ReleaseRow({ r, onOpen, watchlist, toggleWatch }) {
  const premium = r.estimated_market_value
    ? Math.round((r.estimated_market_value / r.retail_price - 1) * 100)
    : null;
  const hue = brandHue(r.brand);
  return (
    <div className="release-row" onClick={() => onOpen(r)}>
      <div className={"row-thumb" + (r.image_url ? " has-img" : "")} style={{ borderLeft: `3px solid oklch(0.75 0.16 ${hue})` }}>
        {r.image_url
          ? <img src={r.image_url} alt={r.name} loading="lazy" onError={(e) => e.currentTarget.parentElement.classList.remove("has-img")} />
          : <span className="row-thumb-init">{brandInitials(r.brand)}</span>}
      </div>
      <div className="row-name">
        <div className="n">{r.name}</div>
        <div className="c">
          <span>{[r.colorway, r.style_code].filter(Boolean).join(" · ") || "—"}</span>
          <SourceLink r={r} compact />
        </div>
      </div>
      <div className="row-date-stack">
        <div className="row-date">{fmtDate(r.release_date, { month: "short", day: "numeric" })}</div>
        <DaysPill days={r.days_until_release} date={r.release_date} />
      </div>
      <div className="row-hype">
        <HypeBadge level={r.hype_level} />
        <div className="row-hype-bar">
          <div className="row-hype-fill" style={{
            width: `${r.hype_score * 10}%`,
            background: r.hype_score >= 9 ? "var(--extreme)" : r.hype_score >= 7 ? "var(--high)" : r.hype_score >= 4 ? "var(--medium)" : "var(--low)"
          }} />
        </div>
      </div>
      <div className="row-method">{r.sale_method}</div>
      <div className="row-price-stack">
        <div className="row-price">${r.retail_price?.toFixed(0) ?? "—"}</div>
        {premium != null && <div className="row-mv">MV ${r.estimated_market_value} <span className="up">+{premium}%</span></div>}
      </div>
      <WatchBtn id={r.id} watchlist={watchlist} toggleWatch={toggleWatch} />
    </div>
  );
}

// ── Feed row ─────────────────────────────────────────────────
function FeedRow({ r, onOpen, watchlist, toggleWatch }) {
  return (
    <div className="feed-row" onClick={() => onOpen(r)}>
      <div className={"feed-img" + (r.image_url ? " has-img" : "")}>
        {r.image_url && <img src={r.image_url} alt={r.name} loading="lazy" onError={(e) => e.currentTarget.parentElement.classList.remove("has-img")} />}
      </div>
      <div className="feed-body">
        <div className="feed-meta">
          <BrandChip brand={r.brand} />
          <DaysPill days={r.days_until_release} date={r.release_date} />
          <HypeBadge level={r.hype_level} score={r.hype_score} />
          <span className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>
            {fmtFullDate(r.release_date)} · {r.sale_method}
          </span>
          <SourceLink r={r} />
        </div>
        <div className="feed-name">{r.name}</div>
        {(r.colorway || r.style_code) && <div className="release-colorway">{[r.colorway, r.style_code].filter(Boolean).join(" · ")}</div>}
        <div className="feed-foot">
          <div className="release-price"><span className="currency">$</span>{r.retail_price?.toFixed(0) ?? "TBD"}</div>
          {r.estimated_market_value && (
            <div className="release-mv">MV <span className="up">${r.estimated_market_value}</span> · resell premium {Math.round((r.estimated_market_value/r.retail_price - 1) * 100)}%</div>
          )}
          <div style={{ marginLeft: "auto" }}>
            <WatchBtn id={r.id} watchlist={watchlist} toggleWatch={toggleWatch} size={16} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ── List/Grid/Feed renderer ──────────────────────────────────
function ReleaseList({ rows, view, onOpen, watchlist, toggleWatch }) {
  if (!rows.length) {
    return (
      <div className="empty">
        <div className="e-title">Nothing matches.</div>
        <div className="muted-text">Try clearing some filters.</div>
      </div>
    );
  }
  if (view === "grid") {
    return (
      <div className="grid-3">
        {rows.map(r => <ReleaseCard key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
      </div>
    );
  }
  if (view === "feed") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {rows.map(r => <FeedRow key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
      </div>
    );
  }
  // list
  return (
    <div className="release-list">
      <div className="release-list-head">
        <div></div>
        <div>Name</div>
        <div>Date</div>
        <div>Hype</div>
        <div>Method</div>
        <div style={{ textAlign: "right" }}>Price</div>
        <div></div>
      </div>
      {rows.map(r => <ReleaseRow key={r.id} r={r} onOpen={onOpen} watchlist={watchlist} toggleWatch={toggleWatch} />)}
    </div>
  );
}

// ── Donut chart ──────────────────────────────────────────────
function HypeDonut({ counts }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const tiers = [
    { k: "EXTREME", color: "var(--extreme)" },
    { k: "HIGH",    color: "var(--high)" },
    { k: "MEDIUM",  color: "var(--medium)" },
    { k: "LOW",     color: "var(--low)" },
  ];
  const r = 56, c = 70, circ = 2 * Math.PI * r;
  let offset = 0;
  return (
    <div className="donut-wrap">
      <div className="donut">
        <svg viewBox="0 0 140 140">
          <circle cx={c} cy={c} r={r} fill="none" stroke="var(--surface-3)" strokeWidth="14" />
          {tiers.map(t => {
            const v = counts[t.k] || 0;
            const len = (v / total) * circ;
            const dash = `${len} ${circ - len}`;
            const el = (
              <circle key={t.k}
                cx={c} cy={c} r={r}
                fill="none" stroke={t.color}
                strokeWidth="14"
                strokeDasharray={dash}
                strokeDashoffset={-offset}
                style={{ transition: "stroke-dashoffset 0.6s, stroke-dasharray 0.6s" }}
              />
            );
            offset += len;
            return el;
          })}
        </svg>
        <div className="donut-center">
          <div>
            <div className="donut-total">{total}</div>
            <div className="donut-label">Releases</div>
          </div>
        </div>
      </div>
      <div className="donut-legend">
        {tiers.map(t => {
          const v = counts[t.k] || 0;
          const p = Math.round((v / total) * 100);
          return (
            <div key={t.k} className="donut-legend-row">
              <span className="sw" style={{ background: t.color }}></span>
              <span className="l">{t.k.charAt(0) + t.k.slice(1).toLowerCase()}</span>
              <span className="v">{v}</span>
              <span className="p">{p}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Brand bar chart ──────────────────────────────────────────
function BrandBars({ releases, max = 8 }) {
  const counts = {};
  releases.forEach(r => { counts[r.brand] = (counts[r.brand] || 0) + 1; });
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, max);
  const peak = top[0]?.[1] || 1;
  return (
    <div className="bar-chart">
      {top.map(([b, n]) => (
        <div key={b} className="bar-row">
          <div className="l">{b}</div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${(n / peak) * 100}%`, background: `oklch(0.78 0.18 ${brandHue(b)})` }} />
          </div>
          <div className="v">{n}</div>
        </div>
      ))}
    </div>
  );
}

// ── Toast helper ─────────────────────────────────────────────
function ToastStack({ toasts }) {
  return (
    <div className="toast-stack">
      {toasts.map(t => (
        <div key={t.id} className="toast">
          <span className="t-icon"><Icons.Check size={14} /></span>
          {t.text}
        </div>
      ))}
    </div>
  );
}

// Export
Object.assign(window, {
  Icons, Icon,
  fmtDate, fmtFullDate, daysLabel, daysClass, brandInitials, brandHue,
  HypeBadge, DaysPill, BrandChip, WatchBtn, SourceLink, Sparkline,
  ReleaseCard, ReleaseRow, FeedRow, ReleaseList,
  HypeDonut, BrandBars, ToastStack,
});
