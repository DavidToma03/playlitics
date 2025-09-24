# 🎮 Playlitics — Streamlit Data Storytelling Dashboard

An interactive dashboard for exploring a synthetic video games dataset (or your own CSV). Built with Streamlit, Plotly, and Pandas.

> Live demo: (add your Streamlit Cloud URL here)

![CI](https://img.shields.io/badge/CI-pending-lightgrey)

## Features
- Sidebar filters: year, genres, platforms, price
- KPI cards (games, avg metascore, avg user score, median price)
- Charts: price vs metascore scatter (colored by user score), owners by year boxplot, top genres bar, hours vs metascore heatmap
- Insights panel: 2–3 auto-generated bullet insights from current filters
- CSV/JSON download for filtered data
- Upload your own CSV (best effort column mapping)

## Quickstart (Windows PowerShell)

```powershell
# 1) Create and activate a virtual environment
py -3 -m venv .venv
. .venv\Scripts\Activate.ps1

# 2) Install requirements
pip install -r requirements.txt

# 3) Run the app
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## Dataset
By default, the app generates a deterministic synthetic dataset with columns like:
- genre, platform, release_year, price, metascore, user_score, hours_played, owners_millions, is_multiplayer

You can also upload a CSV with similar columns; some common aliases are auto-mapped (e.g., `metacritic` -> `metascore`).

## Tests
Minimal tests cover the insights helper.

```powershell
pytest -q
```

## Project structure
- `app.py` — Streamlit app
- `src/data.py` — dataset generator and CSV reader
- `src/insights.py` — KPI and text insights helpers
- `tests/` — unit tests
- `.streamlit/config.toml` — theme and Streamlit config

## Next ideas
- Add a small predictive model (e.g., predict user_score from price/genre/year) with a slider-based what-if panel
- Add caching of uploaded datasets and session-based bookmarks
- Export chart as PNG/GIF

---
Made for internships/placements: shows data skills, interactive UI, and clear storytelling.

## Portfolio polish checklist
- Deploy a live demo (Streamlit Community Cloud or Render) and add the link at the top of this README.
- Record a 60–90 second screen capture (no audio needed) showing filters, charts, and insights updating; place a GIF in the README.
- Add 3–5 unit tests and a CI badge (GitHub Actions running `pytest` on push).
- Include a short “What I learned” section: caching, interactive UX, and how insights are computed.
- Tag the repository with topics: `streamlit`, `visualization`, `pandas`, `plotly`, `data-storytelling`.
