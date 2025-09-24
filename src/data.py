from __future__ import annotations

import io
import hashlib
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


def _seed_from_string(s: str) -> int:
    """seed from string using SHA256."""
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


@dataclass(frozen=True)
class DatasetConfig:
    n_rows: int = 2000
    random_seed: Optional[int] = None


def generate_games_dataset(cfg: DatasetConfig = DatasetConfig()) -> pd.DataFrame:
    """Generate a fake games dataset.

    Columns:
    - game_id: int
    - title: str
    - genre: category
    - platform: category
    - release_year: int
    - price: float
    - metascore: int (0-100)
    - user_score: float (0-10)
    - hours_played: float (0-300)
    - owners_millions: float (0-50)
    - is_multiplayer: bool
    """
    n = cfg.n_rows
    seed = cfg.random_seed if cfg.random_seed is not None else _seed_from_string(f"rows={n}")
    rng = np.random.default_rng(seed)

    genres = np.array([
        "Action", "Adventure", "RPG", "Strategy", "Simulation",
        "Sports", "Racing", "Indie", "Puzzle", "Horror",
    ])
    platforms = np.array(["PC", "PlayStation", "Xbox", "Switch", "Mobile"])

    genre = rng.choice(genres, size=n, p=np.array([0.18,0.1,0.15,0.08,0.08,0.1,0.07,0.14,0.06,0.04]))
    platform = rng.choice(platforms, size=n, p=np.array([0.45,0.2,0.18,0.12,0.05]))
    release_year = rng.integers(2005, 2025, size=n)

    base_price = {
        "PC": 40, "PlayStation": 55, "Xbox": 55, "Switch": 50, "Mobile": 5
    }
    price_noise = rng.normal(0, 10, size=n)
    price = np.clip(
        np.array([base_price[p] for p in platform]) + price_noise + (release_year - 2015) * 0.8,
        0.99, 120.0
    )

    metascore = np.clip(
        (70
         + (genre == "Indie") * 5
         + (genre == "RPG") * 3
         + rng.normal(0, 12, size=n)),
        40, 96
    ).round().astype(int)

    user_score = np.clip(
        metascore / 10.0 + rng.normal(0, 1.2, size=n) + (price < 20) * 0.6,
        1.0, 9.7
    )

    hours_played = np.clip(
        rng.gamma(shape=2.0, scale=15.0, size=n) * (1 + (genre == "RPG") * 0.8 + (genre == "Strategy") * 0.3),
        0.2, 400.0
    )

    owners_millions = np.clip(
        (100 - metascore) * rng.uniform(0.01, 0.15, size=n)
        + (price < 20) * rng.uniform(2, 12, size=n)
        + (platform == "Mobile") * rng.uniform(1, 25, size=n),
        0.01, 60.0
    )

    is_multiplayer = rng.random(size=n) < (0.65 * (genre == "Action") + 0.35 * (genre == "Sports") + 0.15)

    df = pd.DataFrame({
        "game_id": np.arange(1, n + 1),
        "title": [f"Game {i:04d}" for i in range(1, n + 1)],
        "genre": pd.Categorical(genre, categories=genres),
        "platform": pd.Categorical(platform, categories=platforms),
        "release_year": release_year,
        "price": price.round(2),
        "metascore": metascore,
        "user_score": user_score.round(1),
        "hours_played": hours_played.round(1),
        "owners_millions": owners_millions.round(2),
        "is_multiplayer": is_multiplayer,
    })

    return df


def read_uploaded_csv(file_bytes: bytes) -> pd.DataFrame:
    """read a user-uploaded CSV into a dataframe"""
    bio = io.BytesIO(file_bytes)
    df = pd.read_csv(bio)
    # Attempt to standardize column names if likely aliases are found
    rename_map = {
        "metacritic": "metascore",
        "userscore": "user_score",
        "hours": "hours_played",
        "owners": "owners_millions",
        "multiplayer": "is_multiplayer",
        "year": "release_year",
    }
    cols = {c: rename_map.get(c.lower(), c) for c in df.columns}
    df = df.rename(columns=cols)
    return df
