import pandas as pd
from src.insights import kpis, top_categories, generate_text_insights


def tiny_df():
    return pd.DataFrame({
        "genre": ["Action", "RPG", "Action"],
        "platform": ["PC", "PC", "Xbox"],
        "release_year": [2020, 2021, 2022],
        "price": [20.0, 60.0, 40.0],
        "metascore": [80, 75, 85],
        "user_score": [8.5, 7.2, 8.8],
        "hours_played": [50.0, 120.0, 70.0],
        "owners_millions": [10.0, 5.0, 7.0],
    })


def test_kpis():
    df = tiny_df()
    ks = kpis(df)
    assert ks["Games"] == 3
    assert 70 <= ks["Avg Metascore"] <= 90


def test_top_categories():
    df = tiny_df()
    tops = top_categories(df, "genre", 2)
    assert tops[0][0] == "Action" and tops[0][1] == 2


def test_generate_text_insights():
    df = tiny_df()
    ins = generate_text_insights(df)
    assert isinstance(ins, list) and len(ins) > 0
