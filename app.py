from __future__ import annotations

import io
from typing import Optional

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data import DatasetConfig, generate_games_dataset, read_uploaded_csv
from src.insights import kpis, top_categories, generate_text_insights

st.set_page_config(page_title="Playlitics – Data Storytelling Dashboard", page_icon="🎮", layout="wide")

#sidebar
with st.sidebar:
    st.title("🎮 Playlitics")
    st.caption("Explore a synthetic games dataset or upload your own CSV.")

    source = st.radio("Data source", ["Synthetic", "Upload CSV"], horizontal=True)
    n_rows = st.slider("Synthetic rows", 500, 10000, 2000, 500)
    st.divider()
    st.markdown("Filters")

#load data
@st.cache_data(show_spinner=False)
def load_data(source: str, n_rows: int) -> pd.DataFrame:
    if source == "Synthetic":
        return generate_games_dataset(DatasetConfig(n_rows=n_rows))
    else:
        return generate_games_dataset(DatasetConfig(n_rows=2000))

if source == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])  # optional
else:
    uploaded = None

if uploaded is not None:
    try:
        df = read_uploaded_csv(uploaded.getvalue())
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")
        df = load_data("Synthetic", n_rows)
else:
    df = load_data(source, n_rows)

#filters
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    year_min = int(df["release_year"].min()) if "release_year" in df else 2005
    year_max = int(df["release_year"].max()) if "release_year" in df else 2024
with st.sidebar:
    year_range = st.slider("Release year", year_min, year_max, (year_min, year_max))
    genres = sorted(df["genre"].dropna().astype(str).unique()) if "genre" in df else []
    platforms = sorted(df["platform"].dropna().astype(str).unique()) if "platform" in df else []
    sel_genres = st.multiselect("Genres", genres, default=genres[:4])
    sel_platforms = st.multiselect("Platforms", platforms, default=platforms[:3])
    price_max = float(df["price"].max()) if "price" in df else 120.0
    price_range = st.slider("Max price", 0.0, price_max, price_max)

#apply filters
mask = pd.Series(True, index=df.index)
if "release_year" in df:
    mask &= df["release_year"].between(year_range[0], year_range[1])
if "genre" in df and sel_genres:
    mask &= df["genre"].astype(str).isin(sel_genres)
if "platform" in df and sel_platforms:
    mask &= df["platform"].astype(str).isin(sel_platforms)
if "price" in df:
    mask &= df["price"] <= price_range

fdf = df[mask].copy()

#header KPIs
cards = kpis(fdf)
left, mid, right, extra = st.columns(4)
left.metric("Games", f"{cards['Games']:,}")
mid.metric("Avg Metascore", f"{cards['Avg Metascore']:.1f}")
right.metric("Avg User Score", f"{cards['Avg User Score']:.1f}")
extra.metric("Median Price", f"${cards['Median Price']:.2f}")

st.divider()

#charts
c1, c2 = st.columns([1, 1])
with c1:
    if {"price", "metascore", "user_score"}.issubset(fdf.columns):
        fig = px.scatter(
            fdf,
            x="price",
            y="metascore",
            color="user_score",
            hover_data=["title", "genre", "platform"],
            color_continuous_scale="Viridis",
            title="Price vs Metascore (color: User Score)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough columns for this chart.")

with c2:
    if {"release_year", "owners_millions"}.issubset(fdf.columns):
        fig = px.box(
            fdf,
            x="release_year",
            y="owners_millions",
            color="platform" if "platform" in fdf else None,
            title="Owners by Release Year",
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

#charts
c3, c4 = st.columns([1, 1])
with c3:
    if "genre" in fdf:
        topg = top_categories(fdf, "genre", 7)
        if topg:
            tg_df = pd.DataFrame(topg, columns=["genre", "count"])
            fig = px.bar(tg_df, x="genre", y="count", title="Top Genres (count)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Genre column not available")

with c4:
    if {"hours_played", "metascore"}.issubset(fdf.columns):
        fig = px.density_heatmap(
            fdf,
            x="metascore",
            y="hours_played",
            nbinsx=24,
            nbinsy=24,
            color_continuous_scale="Magma",
            title="Hours Played vs Metascore (density)",
        )
        st.plotly_chart(fig, use_container_width=True)

#insights
with st.expander("Insights", expanded=True):
    for text in generate_text_insights(fdf):
        st.markdown(f"- {text}")

#data preview and download
st.divider()
st.subheader("Data preview")
st.dataframe(fdf.head(50), use_container_width=True)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        label="Download filtered CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="games_filtered.csv",
        mime="text/csv",
    )
with col_dl2:
    st.download_button(
        label="Download chart data (JSON)",
        data=fdf.to_json(orient="records").encode("utf-8"),
        file_name="games_filtered.json",
        mime="application/json",
    )

st.caption("Tip: Use the sidebar to tweak filters. Upload your own CSV to explore another dataset.")
