import pandas as pd
from pathlib import Path
from src.prices import (
    download_price_data,
    get_previous_trading_day,
    get_next_trading_day_on_or_after,
    get_price_on_date)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def build_trade_table(score_threshold: float = 0.02, entry_days_before: int = 28):
    pipeline_path = PROCESSED_DIR / "pipeline_scores.csv"
    catalysts_path = PROCESSED_DIR / "catalysts.csv"

    pipeline_df = pd.read_csv(pipeline_path)
    catalysts_df = pd.read_csv(catalysts_path)

    catalysts_df["catalyst_date"] = pd.to_datetime(catalysts_df["catalyst_date"])

    merged = catalysts_df.merge(
        pipeline_df[["ticker", "pipeline_score"]], # only take these 2 columns
        on="ticker",
        how="left"
    )

    merged = merged.copy()

    tickers = merged["ticker"].dropna().unique().tolist()
    price_data = download_price_data(tickers)

    trade_rows = []

    for _, row in merged.iterrows():
        ticker = row["ticker"]
        catalyst_date = row["catalyst_date"]
        pipeline_score = row["pipeline_score"]

        if ticker not in price_data:
            continue

        price_df = price_data[ticker]

        raw_entry_date = catalyst_date - pd.Timedelta(days=entry_days_before)

        entry_date = get_next_trading_day_on_or_after(price_df, raw_entry_date)
        exit_date = get_previous_trading_day(price_df, catalyst_date)

        if entry_date is None or exit_date is None:
            continue
        if entry_date >= exit_date:
            continue

        entry_price = get_price_on_date(price_df, entry_date)
        exit_price = get_price_on_date(price_df, exit_date)

        if entry_price is None or exit_price is None:
            continue

        trade_return = (exit_price / entry_price) - 1

        trade_rows.append({
            "ticker": ticker,
            "catalyst date": catalyst_date,
            "entry date": entry_date,
            "exit date": exit_date,
            "entry price": entry_price,
            "exit price": exit_price,
            "trade return": trade_return,
            "pipeline score": pipeline_score
        })
    
    trades_df = pd.DataFrame(trade_rows)

    if not trades_df.empty:
        trades_df = trades_df.sort_values(["entry date", "ticker"]).reset_index(drop=True)
        trades_df["trade return"] = trades_df["trade return"].round(4)
        trades_df["pipeline score"] = trades_df["pipeline score"].round(3)

    return trades_df


def main():
    trades_df = build_trade_table(score_threshold=0.02, entry_days_before=28)

    output_path = PROCESSED_DIR / "trades.csv"
    trades_df.to_csv(output_path, index=False)

    print("\nSaved trade table to: ")
    print(output_path) # shows like file pathway

    if trades_df.empty:
        print("\nNo trades were generated.")
    else:
        print("\nSample trades: ")
        print(trades_df.head())

if __name__ == "__main__":
    main()