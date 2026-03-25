# Sneaker Release Tracker

A live dashboard tracking major sneaker releases over the next 90 days, with automated hype scoring, sale method classification, and release calendar views.

**[→ Open the Dashboard](https://lordnader2002-sudo.github.io/Shoe-Tracker-v2/)**

Data refreshes automatically **every day at 1:00 AM EST**.

---

## Pages

### Summary
An at-a-glance overview of the full release calendar.

| Section | Description |
|---|---|
| **Stats Bar** | Total upcoming releases, drops this week, HIGH and EXTREME counts |
| **Top Hype Releases** | The 6 highest-scoring releases, with hype level and sale method |
| **Dropping This Week** | All releases within the next 7 days, with hype level and sale method |
| **Brand Breakdown** | Five charts: releases by brand, sale method, hype level, price range, and release month |
| **Hype Score** | Explanation of the scoring methodology and how each factor is weighted |
| **Quick Links** | Navigation to other pages and the Excel report download |

---

### Releases
The complete release list for the next 90 days.

- Search by name with instant filtering
- Filter by brand or hype level
- Sort by release date, hype score, or retail price
- Card grid and compact list views
- Color-coded urgency for releases dropping this week vs. later

---

### Calendar
A monthly calendar with every release plotted on its release date.

- Up to 4 shoe names per day tile, with an overflow count for busier days
- Left-border color reflects hype level
- Click any day for a full detail panel with prices, scores, and sale method
- Month navigation with previous/next controls

---

### Hype Watch
Only HIGH and EXTREME releases, sorted by score descending. Intended as a focused view for high-demand drops.

---

## Hype Scores

Each release is scored from 1 to 10 and assigned one of four tiers:

| Level | Score | Description |
|---|---|---|
| **LOW** | 1–3 | Widely available, low secondary market demand |
| **MEDIUM** | 4–6 | Moderate demand, some sell-out risk |
| **HIGH** | 7–8 | Elevated demand, likely to sell out quickly |
| **EXTREME** | 9–10 | Very high demand, significant resell premium expected |

### Scoring factors

**Resell Premium — 50% of score (35% when no market data is available)**
Measures how much the shoe is expected to trade above retail. Above 300% of retail scores 10; above 100% scores 8; at or below retail scores 1. When no resell data is available, this factor is omitted and the remaining three carry more weight.

**Brand — 20% of score (35% without resell data)**

| Brand | Score |
|---|---|
| Jordan, Yeezy | 9 |
| Nike | 7 |
| New Balance | 6 |
| Adidas, Converse | 5 |
| HOKA, On | 3 |

**Silhouette — 20% of score (45% without resell data)**
High-demand models (AJ1, AJ4, Dunk, Yeezy 350, NB 990) score 9. Mid-tier models (AJ12, Vapormax, Blazer) score 6. All others score 3.

**Collaboration — 10% of score (20% without resell data)**
Shoes with a notable collaborator (Travis Scott, Off-White, Supreme, Sacai, Bad Bunny, and similar) score 10 for this factor.

---

## Sale Methods

Each release is classified by how it will be sold:

| Method | Description |
|---|---|
| **Online + Retail** | Available through standard online and in-store channels |
| **SNKRS App** | Nike SNKRS App exclusive |
| **Confirmed App** | Adidas Confirmed App exclusive |
| **Raffle/Dropship** | Entry-based draw, selected retailers |
| **Giveaway** | Promotional release |
| **In-Store** | In-store only |
| **Retail** | Standard retail, broad distribution |

---

## Excel Report

A downloadable `.xlsx` file is generated with each data refresh and contains three tabs:

| Tab | Contents |
|---|---|
| **All Releases** | Complete list with all fields |
| **High Hype Alerts** | HIGH and EXTREME releases only |
| **Summary** | Counts by brand and hype level |

Available via the **Download Excel Report** link on any page.

---

## Data Pipeline

```
Every day at 1:00 AM EST
        │
        ▼
  Scrapes 3 sneaker sites
  (SneakerFiles, NiceKicks, SneakerBarDetroit)
        │
        ▼
  Deduplicates and normalises records
        │
        ▼
  Calculates hype scores and classifies sale method
        │
        ▼
  Generates releases.json and Excel report
        │
        ▼
  Publishes to GitHub Pages
```

The "Updated" timestamp in the top-right corner of the dashboard reflects the exact time of the last refresh.

---

## Data Sources

| Source | URL |
|---|---|
| SneakerFiles | sneakerfiles.com/release-dates |
| NiceKicks | nicekicks.com/sneaker-release-dates |
| SneakerBar Detroit | sneakerbardetroit.com/sneaker-release-dates |

Duplicates across sources are removed automatically; one canonical record is kept per release.

