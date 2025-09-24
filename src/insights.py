from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Compute key metrics for header cards."""
    return {
        "Games": int(len(df)),
        "Avg Metascore": float(df["metascore"].mean()) if "metascore" in df else float("nan"),
        "Avg User Score": float(df["user_score"].mean()) if "user_score" in df else float("nan"),
        "Median Price": float(df["price"].median()) if "price" in df else float("nan"),
    }


def top_categories(df: pd.DataFrame, col: str, n: int = 5) -> List[Tuple[str, int]]:
    if col not in df:
        return []
    vc = df[col].astype(str).value_counts().head(n)
    return list(zip(vc.index.tolist(), vc.values.tolist()))


def generate_text_insights(df: pd.DataFrame) -> List[str]:
    """Return 2-3 punchy, data-backed insights as strings."""
    insights: List[str] = []
    if len(df) == 0:
        return ["No data available — adjust filters or upload a dataset."]

    # 1) Best-value genre by hours per dollar
    if {"hours_played", "price", "genre"}.issubset(df.columns):
        agg = (
            df[df["price"] > 0]
            .groupby("genre", dropna=False, observed=False)
            .apply(lambda g: (g["hours_played"].mean()) / (g["price"].mean()))
            .sort_values(ascending=False)
        )
        if len(agg) > 0:
            g, v = agg.index[0], agg.iloc[0]
            insights.append(
                f"Best value: {g} offers ~{v:.1f} hours per $1 on average."
            )

    # 2) Price vs. ratings correlation
    if {"price", "user_score", "metascore"}.issubset(df.columns):
        corr_user = df[["price", "user_score"]].corr().iloc[0, 1]
        corr_meta = df[["price", "metascore"]].corr().iloc[0, 1]
        insights.append(
            f"Correlation: price vs user score {corr_user:+.2f}, price vs metascore {corr_meta:+.2f}."
        )

    # 3) Platform with highest owners (popularity proxy)
    if {"platform", "owners_millions"}.issubset(df.columns):
        pop = (
            df.groupby("platform", dropna=False, observed=False)["owners_millions"]
            .mean()
            .sort_values(ascending=False)
        )
        if len(pop) > 0:
            p, val = pop.index[0], pop.iloc[0]
            insights.append(
                f"Most popular platform by owners: {p} (~{val:.1f}M average)."
            )

    # Keep only 3 nuggets
    return insights[:3]
