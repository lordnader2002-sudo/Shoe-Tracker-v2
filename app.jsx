// Main app shell — sidebar nav, topbar, view router

const { useState: useStateA, useEffect: useEffectA, useMemo: useMemoA } = React;

function App() {
  // Persisted defaults via tweaks panel
  const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
    "theme": "dark",
    "density": "comfortable",
    "defaultView": "grid"
  } /*EDITMODE-END*/;

  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [page, setPage] = useStateA("summary");
  const [search, setSearch] = useStateA("");
  const [view, setView] = useStateA(tweaks.defaultView || "grid");
  const [watchlist, setWatchlist] = useStateA(() => new Set());
  const [openRel, setOpenRel] = useStateA(null);
  const [toasts, setToasts] = useStateA([]);

  useEffectA(() => {
    document.documentElement.setAttribute("data-theme", tweaks.theme);
    document.documentElement.setAttribute("data-density", tweaks.density);
  }, [tweaks.theme, tweaks.density]);

  useEffectA(() => {setView(tweaks.defaultView || "grid");}, [tweaks.defaultView]);

  const releases = window.RELEASES;

  const counts = useMemoA(() => ({
    summary: releases.length,
    releases: releases.length,
    calendar: releases.length,
    hype: releases.filter((r) => r.hype_level === "HIGH" || r.hype_level === "EXTREME").length,
    brands: Object.keys(window.BRAND_META).length,
    watchlist: watchlist.size
  }), [releases, watchlist]);

  function toggleWatch(id) {
    setWatchlist((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        pushToast("Removed from watchlist");
      } else {
        next.add(id);
        pushToast("Saved to watchlist");
      }
      return next;
    });
  }

  function pushToast(text) {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, text }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 2200);
  }

  const navigate = (p) => {setPage(p);window.scrollTo({ top: 0, behavior: "smooth" });};

  const NAV = [
  { k: "summary", label: "Summary", icon: Icons.Sparkles },
  { k: "releases", label: "Releases", icon: Icons.Layers },
  { k: "calendar", label: "Calendar", icon: Icons.Calendar },
  { k: "hype", label: "Hype Watch", icon: Icons.Flame },
  { k: "brands", label: "Brands", icon: Icons.Tag },
  { k: "watchlist", label: "Watchlist", icon: Icons.Bookmark }];


  const pageTitleMap = {
    summary: "Summary",
    releases: "Releases",
    calendar: "Calendar",
    hype: "Hype Watch",
    brands: "Brands",
    watchlist: "Watchlist"
  };

  return (
    <div className="app">
      {/* ─── Sidebar ─── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">/S</div>
          <div>
            <div className="brand-name">Sneaker Tracker</div>
            <div className="brand-sub">V2.4</div>
          </div>
        </div>

        <div className="nav-section-label">Discover</div>
        {NAV.slice(0, 4).map((n) =>
        <button key={n.k} className={`nav-item ${page === n.k ? "active" : ""}`} onClick={() => navigate(n.k)}>
            <span className="nav-icon"><n.icon size={15} /></span>
            <span>{n.label}</span>
            <span className="nav-count">{counts[n.k]}</span>
          </button>
        )}

        <div className="nav-section-label">Personal</div>
        {NAV.slice(4).map((n) =>
        <button key={n.k} className={`nav-item ${page === n.k ? "active" : ""}`} onClick={() => navigate(n.k)}>
            <span className="nav-icon"><n.icon size={15} /></span>
            <span>{n.label}</span>
            <span className="nav-count">{counts[n.k]}</span>
          </button>
        )}

        <div className="sidebar-footer">
          <div className="sidebar-meta">
            <div className="sidebar-meta-row"><span>Last sync</span><span className="v">{window.GENERATED_AT.split(",")[1]?.trim() || "now"}</span></div>
            <div className="sidebar-meta-row"><span>Sources</span><span className="v">3 active</span></div>
            <div className="sidebar-meta-row"><span>Refresh</span><span className="v">Daily 1AM EST</span></div>
          </div>
        </div>
      </aside>

      {/* ─── Main ─── */}
      <main className="main">
        <header className="topbar">
          <div className="topbar-title">{pageTitleMap[page]}<span className="topbar-sub">/ {window.GENERATED_AT}</span></div>
          <div className="topbar-search">
            <span className="icon-search"><Icons.Search size={14} /></span>
            <input
              type="text"
              placeholder="Search by name, colorway, or style code…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onFocus={() => page !== "releases" && setPage("releases")} />
            
          </div>
        </header>

        {page === "summary" && <SummaryView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} navigate={navigate} />}
        {page === "releases" && <ReleasesView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} view={view} setView={setView} search={search} />}
        {page === "calendar" && <CalendarView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} />}
        {page === "hype" && <HypeWatchView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} />}
        {page === "brands" && <BrandsView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} />}
        {page === "watchlist" && <WatchlistView releases={releases} onOpen={setOpenRel} watchlist={watchlist} toggleWatch={toggleWatch} />}
      </main>

      {openRel && <DetailModal release={openRel} onClose={() => setOpenRel(null)} watchlist={watchlist} toggleWatch={toggleWatch} />}
      <ToastStack toasts={toasts} />

      <TweaksPanel title="Tweaks">
        <TweakSection title="Appearance">
          <TweakRadio
            label="Theme"
            value={tweaks.theme}
            onChange={(v) => setTweak("theme", v)}
            options={[{ value: "dark", label: "Dark" }, { value: "light", label: "Light" }]} />
          
          <TweakRadio
            label="Density"
            value={tweaks.density}
            onChange={(v) => setTweak("density", v)}
            options={[
            { value: "compact", label: "Compact" },
            { value: "comfortable", label: "Comfy" },
            { value: "spacious", label: "Spacious" }]
            } />
          
        </TweakSection>
        <TweakSection title="Layout">
          <TweakRadio
            label="Default list view"
            value={tweaks.defaultView}
            onChange={(v) => setTweak("defaultView", v)}
            options={[
            { value: "grid", label: "Grid" },
            { value: "list", label: "List" },
            { value: "feed", label: "Feed" }]
            } />
          
        </TweakSection>
      </TweaksPanel>
    </div>);

}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);