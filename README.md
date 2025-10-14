
# SOFEA — High‑Fidelity Dashboard Mockup (Static Data)

This is a **clickable mockup** for donors/devs to explore the final look & drilldowns. It runs on **fake static data**.

## Run locally
```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:8050
```

## Deploy to Render (quickest)
1. Push these files to a GitHub repo.
2. In Render → *New +* → *Web Service* → connect the repo.
3. Environment: **Python 3.11+**
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:server`
6. Click *Deploy*.

## Notes
- Pages: Overview, AIS, EIS, HIS, SIS, Awardee Explorer, & Awardee Detail (via clicking a bar on Overview).
- Dark-first theme, brand color `#4c00b0`.
