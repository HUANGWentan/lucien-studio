# Lucien Studio

🌿 AI Consulting landing page for [lucium.io](https://lucium.io).

## Structure

```
├── index.html          # Main landing page
├── server.py           # Flask server (static + article proxy)
├── pages/
│   ├── ai-news-latest.html    # Daily AI news brief
│   └── xpeng-p7plus-erev.html # Research pages
├── img/                # Background photography
└── .gitignore
```

## Deploy

```bash
pip install flask trafilatura requests
python server.py
```

Serves on `http://localhost:8080` — pair with nginx + Let's Encrypt for production.

## Design

Built with:
- Playfair Display + DM Sans typeface
- Full-bleed photography backgrounds
- Glassmorphism hover states on hover
- SVG grain texture overlay
- Fully responsive

## Daily AI News

Auto-generated every day at 11:00 AM (China time) via Hermes Agent cron.
