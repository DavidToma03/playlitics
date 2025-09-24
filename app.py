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

    source = st.radio(
        "Data source",
        ["Synthetic", "Upload CSV"],
        horizontal=True,
        key="source",
    )
    if source == "Synthetic":
        n_rows = st.slider(
            "Synthetic rows",
            500,
            10000,
            2000,
            500,
            help="Number of rows to generate for the synthetic dataset.",
            key="n_rows",
        )
    else:
        #keep a value in state
        n_rows = st.session_state.get("n_rows", 2000)
    # Dark mode toggle
    dark_mode = st.toggle("Dark mode", value=st.session_state.get("dark_mode", False), key="dark_mode")
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
    with st.sidebar:
        uploaded = st.file_uploader("Upload CSV", type=["csv"])  # optional
        with st.expander("CSV guidance"):
            st.markdown(
                "- Expected columns (any subset works, charts adapt):\n"
                "  `title`, `genre`, `platform`, `release_year`, `price`, `metascore`, `user_score`, `hours_played`, `owners_millions`, `is_multiplayer`.\n"
                "- Common aliases like `metacritic`→`metascore`, `userscore`→`user_score`, `owners`→`owners_millions` are auto-mapped.\n"
                "- Numeric columns are auto-coerced when possible."
            )
        sample_df = generate_games_dataset(DatasetConfig(n_rows=100))
        st.download_button(
            label="Download sample CSV (100 rows)",
            data=sample_df.to_csv(index=False).encode("utf-8"),
            file_name="playlitics_sample.csv",
            mime="text/csv",
            help="Use this as a reference for your own data.",
        )
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

# Apply optional dark mode styles and set plotly template
plotly_template = "plotly_dark" if st.session_state.get("dark_mode") else "plotly_white"
if st.session_state.get("dark_mode"):
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #e0e0e0; }
        section[data-testid="stSidebar"] { background-color: #111418; }
        .st-emotion-cache-16idsys p, .stMarkdown, .st-emotion-cache-10trblm p {
            color: #e0e0e0 !important;
        }
        .stMetric { background: rgba(255,255,255,0.03); border-radius: 8px; padding: 0.25rem 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

#filters
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    year_min = int(df["release_year"].min()) if "release_year" in df else 2005
    year_max = int(df["release_year"].max()) if "release_year" in df else 2024
with st.sidebar:
    year_range = st.slider(
        "Release year",
        year_min,
        year_max,
        (year_min, year_max),
        key="year_range",
    )
    genres = sorted(df["genre"].dropna().astype(str).unique()) if "genre" in df else []
    platforms = (
        sorted(df["platform"].dropna().astype(str).unique()) if "platform" in df else []
    )
    #default to all values
    sel_genres = st.multiselect(
        "Genres",
        genres,
        default=genres,
        key="sel_genres",
    )
    sel_platforms = st.multiselect(
        "Platforms",
        platforms,
        default=platforms,
        key="sel_platforms",
    )
    price_max = float(df["price"].max()) if "price" in df else 120.0
    price_range = st.slider(
        "Max price",
        0.0,
        price_max,
        price_max,
        key="price_range",
    )

    #resetting filters
    def _reset_filters():
        st.session_state["year_range"] = (year_min, year_max)
        st.session_state["sel_genres"] = genres
        st.session_state["sel_platforms"] = platforms
        st.session_state["price_range"] = price_max

    st.button("Reset filters", on_click=_reset_filters, type="secondary")

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

#if empty
if len(fdf) == 0:
    st.warning("No rows match the current filters. Try resetting or broadening filters.")
    st.stop()

#header KPIs
cards = kpis(fdf)
#active filters
active_filters = []
if (year_range[0], year_range[1]) != (year_min, year_max):
    active_filters.append(f"Year: {year_range[0]}–{year_range[1]}")
if sel_genres and len(sel_genres) < len(genres):
    active_filters.append(f"Genres: {len(sel_genres)} selected")
if sel_platforms and len(sel_platforms) < len(platforms):
    active_filters.append(f"Platforms: {len(sel_platforms)} selected")
if price_range < price_max:
    active_filters.append(f"Max price: ${price_range:.0f}")

if active_filters:
    st.caption("Active filters — " + ", ".join(active_filters))
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
            template=plotly_template,
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
            template=plotly_template,
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
            fig = px.bar(tg_df, x="genre", y="count", title="Top Genres (count)", template=plotly_template)
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
            template=plotly_template,
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
