import pandas as pd
import yfinance as yf
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

def download_price_data(tickers: list[str], start_date: str = "2020-01-01", end_date: str = "2025-12-31"):
    price_data = {}

    for ticker in tickers:
        print(f"Dowloading prices for {ticker}...")
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)

        if df.empty:
            print(f"No price data found for {ticker}...")
            continue

        df = df.reset_index()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        price_data[ticker] = df

    return price_data

def get_previous_trading_day(price_df: pd.DataFrame, target_date: pd.Timestamp):
    # exit date: 1 day before catalyst
    valid_days = price_df[price_df["Date"] < target_date]
    if valid_days.empty:
        return None
    return valid_days.iloc[-1]["Date"]

def get_next_trading_day_on_or_after(price_df: pd.DataFrame, target_date: pd.Timestamp):
    # entry date (first trading day on/after target_date)
    valid_days = price_df[price_df["Date"] >= target_date]
    if valid_days.empty:
        return None
    return valid_days.iloc[0]["Date"]

def get_price_on_date(price_df: pd.DataFrame, target_date: pd.Timestamp, price_col: str = "Adj Close"):
    row = price_df[price_df["Date"] == target_date]
    if row.empty:
        return None
    return float(row.iloc[0][price_col])