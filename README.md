# Playlitics

An interactive dashboard for exploring a synthetic video games dataset (or your own).

## Features
- Sidebar filters: year, genres, platforms, price
- KPI cards (games, avg metascore, avg user score, median price)
- Charts: price vs metascore scatter (colored by user score), owners by year boxplot, top genres bar, hours vs metascore heatmap
- Insights panel: 2–3 auto-generated bullet insights from current filters
- CSV/JSON download for filtered data
- Upload your own CSV

## Quickstart (Windows PowerShell)

```powershell
py -3 -m venv .venv
. .venv\Scripts\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## Dataset
By default, the app generates a deterministic synthetic dataset with columns like:
- genre, platform, release_year, price, metascore, user_score, hours_played, owners_millions, is_multiplayer

You can also upload a CSV with similar columns.
