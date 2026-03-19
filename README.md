# 👟 Sneaker Release Tracker

> **Your personal early-warning system for every major sneaker drop.**

---

## 🔗 [→ Open the Dashboard](https://lordnader2002-sudo.github.io/Shoe-Tracker-v2/)

No login. No app to install. Just click and go.

---

## What Is This?

The Sneaker Release Tracker is a live dashboard that shows you every major sneaker dropping in the next 30 days — with a **Hype Score** on each one so you know exactly what to line up for and what you can skip.

It automatically refreshes every **Monday and Friday at 1:00 AM EST**, pulling data from three of the biggest sneaker release calendars on the web and combining them into one clean view.

---

## 🗂️ The Four Pages

### 📊 Summary
Your homepage. A snapshot of everything important at a glance.

| Section | What It Shows |
|---|---|
| **Stats Bar** | Total drops coming up, how many land this week, HIGH and EXTREME hype counts |
| **Top Hype Releases** | The 6 hottest shoes right now, ranked |
| **Dropping This Week** | Every shoe releasing in the next 7 days |
| **Brand Breakdown** | Which brands are dropping the most |
| **How Hype Is Calculated** | Exactly what goes into every shoe's score |
| **Quick Links** | Jump to any other page, or download the Excel report |

---

### 📋 Releases
The full list. Every shoe dropping in the next 30 days, all in one place.

- **Search** by name — type anything and results filter instantly
- **Filter** by brand (Nike, Jordan, Adidas, etc.) or hype level (LOW → EXTREME)
- **Sort** by release date, hype score, or retail price
- **Two views** — a card grid for browsing, or a compact list for scanning fast
- Color-coded urgency indicators show which shoes are **dropping this week** vs. coming up soon

---

### 🗓️ Calendar
A traditional monthly calendar with every drop marked on the right day.

- Each day shows the shoe names directly on the tile (up to 4, then "+X more")
- Left-border color tells you the hype level at a glance
- Click any day to open a full detail panel with images, prices, and hype scores
- Navigate month-by-month with the prev/next arrows

---

### 🔥 Hype Watch
Only the **HIGH** and **EXTREME** releases. No noise, no fillers.

This is your must-watch list — every shoe here has a real chance of selling out fast or carrying strong resell value. Sorted by hype score, highest first.

---

## 🎯 Understanding Hype Scores

Every shoe gets a score from **1 to 10**, broken into four levels:

| Level | Score | What It Means |
|---|---|---|
| 🟢 **LOW** | 1 – 3 | Widely available, shelf filler, easy cop |
| 🔵 **MEDIUM** | 4 – 6 | Some demand, worth keeping an eye on |
| 🟠 **HIGH** | 7 – 8 | Sell out risk is real — move fast |
| 🔴 **EXTREME** | 9 – 10 | All-time heat. Bots, raffles, campouts |

### How the score is calculated

Each shoe is scored on four factors, then blended into a final 1–10 score:

**💰 Resell Premium — up to 50% of the score**
How much the shoe is expected to trade above retail on the secondary market. A shoe sitting flat at retail scores 1/10. One flipping at 3× retail scores 10/10. When no resell data is available, this factor is omitted and the other three carry more weight.

**👟 Brand Factor — up to 20% of the score**
Some brands carry more hype than others, full stop.

| Brand | Rating |
|---|---|
| Jordan, Yeezy | 9 / 10 |
| Nike | 7 / 10 |
| New Balance | 6 / 10 |
| Adidas, Converse | 5 / 10 |
| HOKA, On | 3 / 10 |

**🏆 Silhouette Boost — up to 20% of the score**
The model matters as much as the brand. An Air Jordan 1, Dunk, or Yeezy 350 scores 9/10 regardless of colorway. Mid-tier silhouettes like the Vapormax score 6/10. Everything else gets a 3/10.

**🤝 Collab Boost — up to 10% of the score**
If the shoe is a collaboration with a high-profile name — Travis Scott, Off-White, Supreme, Sacai, Bad Bunny, and others — this factor automatically scores 10/10 and pulls the whole number up.

---

## 📥 Excel Report

Every version of the dashboard includes a downloadable `.xlsx` file with three tabs:

| Tab | Contents |
|---|---|
| **All Releases** | Complete list with all fields, ready to sort and filter |
| **High Hype Alerts** | Only HIGH and EXTREME releases |
| **Summary** | Stats by brand and hype level |

Click **⬇ Excel Report** in the top-right corner of any page, or use the button on the Summary page.

---

## ⚡ How It Stays Up To Date

The tracker runs automatically — no one has to do anything manually.

```
Every Monday & Friday at 1:00 AM EST
        │
        ▼
  Scrapes 3 sneaker sites
  (SneakerFiles, NiceKicks, SneakerBarDetroit)
        │
        ▼
  Deduplicates & cleans the data
        │
        ▼
  Calculates hype scores
        │
        ▼
  Generates JSON + Excel report
        │
        ▼
  Publishes to the dashboard
```

The "Updated" timestamp in the top-right corner of the dashboard always shows the exact moment the last refresh ran.

---

## 🌐 Data Sources

| Source | URL |
|---|---|
| SneakerFiles | sneakerfiles.com/release-dates |
| NiceKicks | nicekicks.com/sneaker-release-dates |
| SneakerBar Detroit | sneakerbardetroit.com/sneaker-release-dates |

When the same shoe appears on multiple sites, duplicates are automatically removed and only one listing is kept.

---

## 🏗️ How It's Built (for the curious)

The project is split into two parts:

**Backend (runs automatically via GitHub Actions)**
- `scraper.py` — fetches and parses release data from three sources
- `hype.py` — calculates hype scores using the multi-factor algorithm
- `excel_export.py` — generates the formatted `.xlsx` download

**Frontend (static website, hosted on GitHub Pages)**
- Pure HTML, CSS, and vanilla JavaScript — no frameworks, no backend needed
- The site loads `releases.json` and renders everything in the browser
- Dark theme with orange accents and Inter font

**Tech stack at a glance:**

| Layer | Tool |
|---|---|
| Scraping | Python + BeautifulSoup |
| Excel Export | openpyxl |
| Automation | GitHub Actions (cron schedule) |
| Hosting | GitHub Pages |
| No database | JSON flat file |

---

## 🗓️ Refresh Schedule

| Day | Time |
|---|---|
| Monday | 1:00 AM EST |
| Friday | 1:00 AM EST |

You can also trigger a manual refresh from the GitHub Actions tab at any time.

---

## 📁 Project Layout

```
Shoe-Tracker-v2/
├── .github/workflows/
│   └── sneaker-tracker.yml   ← automation schedule
├── docs/                     ← the live website
│   ├── index.html            ← Summary page
│   ├── releases.html         ← Full releases list
│   ├── calendar.html         ← Monthly calendar
│   ├── hype.html             ← Hype Watch
│   ├── assets/               ← CSS and JavaScript
│   └── data/                 ← Auto-generated data files
├── reports/                  ← Raw output from each scrape run
├── scraper.py                ← Main scraper
├── hype.py                   ← Hype score engine
├── excel_export.py           ← Excel generator
└── requirements.txt          ← Python dependencies
```

---

*Data refreshed automatically every Monday & Friday · Built for mall operations and sneaker culture*
