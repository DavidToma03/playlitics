import sys
from pathlib import Path

# Ensure project root is on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data import generate_games_dataset
from src.insights import kpis, generate_text_insights


def main():
    try:
        df = generate_games_dataset()
        print("rows cols:", len(df), list(df.columns)[:6])
        print("kpis:", kpis(df))
        print("insights:", generate_text_insights(df)[:2])
    except Exception as e:
        import traceback
        print("Smoke test failed with exception:")
        traceback.print_exc()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
