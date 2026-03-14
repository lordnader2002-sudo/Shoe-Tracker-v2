# 🔥 Sneaker Release Tracker

Dark-mode dashboard tracking Nike, Jordan, Adidas, New Balance, Puma & Under Armour releases with hype scoring, filterable UI, and Excel/CSV export.

## Live Demo (GitHub Pages)

Enable GitHub Pages in repo **Settings → Pages → Source: main branch / root** and the dashboard loads at:
`https://<your-username>.github.io/Shoe-Tracker-v2/`

## Features

| Feature | Details |
|---|---|
| **Multi-source scraper** | SneakerNews · KicksOnFire · SoleCollector |
| **Hype Level (1–5)** | Scored by brand tier, collab keywords, sale method, price |
| **Dashboard** | Dark mode · filter by brand/hype/method · sort · search |
| **Excel export** | 3-sheet dark-mode workbook (Releases · Summary · Legend) |
| **CSV export** | One-click from the static dashboard |
| **GitHub Actions** | Daily scrape at 8 AM UTC + artifacts uploaded |

## Hype Scale

| Level | Label | Meaning |
|---|---|---|
| ⚪ 1 | General Release | Widely available, no rush |
| 🟡 2 | Popular | Sells out but restocks |
| 🟠 3 | Hyped | Sells out in minutes, bots active |
| 🔴 4 | Limited | Raffle/draw required, 2–5× resale |
| 🟣 5 | Grail | Instant global sellout, 5–15× resale |

## Running Locally (full Flask backend)

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

Scrape latest releases:
```bash
python scraper.py
```

## Project Structure

```
index.html          ← Static dashboard (no server needed)
app.py              ← Flask server (full backend)
scraper.py          ← Multi-source scraper
hype.py             ← Hype level calculator
excel_export.py     ← Dark-mode Excel exporter
templates/          ← Flask Jinja2 templates
static/             ← CSS + JS for Flask app
data/               ← Cached releases (JSON)
.github/workflows/  ← CI + daily scrape workflow
```
