# IN PROGRESS / EXPLORATORY ANALYSIS
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def analyze_pipeline_effect():
    trades_path = PROCESSED_DIR / "trades.csv"
    trades_df = pd.read_csv(trades_path)

    if trades_df.empty:
        print("No trades found.")
        return

    # ---- Create score buckets ----
    trades_df["score_bucket"] = pd.qcut(
        trades_df["pipeline score"],
        q=3,
        duplicates="drop"
    )

    # ---- Group and compute stats ----
    grouped = trades_df.groupby("score_bucket")

    summary = grouped["trade return"].agg([
        "count",
        "mean",
        "median"
    ]).rename(columns={
        "count": "num_trades",
        "mean": "avg_return",
        "median": "median_return"
    })

    # ---- Win rate ----
    win_rate = grouped["trade return"].apply(lambda x: (x > 0).mean())
    summary["win_rate"] = win_rate

    summary = summary.round(4)

    print("\nPipeline Score Analysis:")
    print(summary.to_string())

    return summary


if __name__ == "__main__":
    analyze_pipeline_effect()