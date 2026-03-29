import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def compute_max_drawdown(equity_curve: pd.Series): # computes max drawdown from an equity curve
    running_max = equity_curve.cummax()
    drawdown = (equity_curve / running_max) - 1
    return drawdown.min()

def evaluate_trades(trades_df: pd.DataFrame):
    if trades_df.empty:
        return {
            "total_trades": 0,
            "win_rate": np.nan,
            "average_return": np.nan,
            "median_return": np.nan,
            "cumulative_return": np.nan,
            "sharpe_ratio":np.nan,
            "max_drawdown": np.nan
        }
    
    returns = trades_df["trade return"].copy() # is a pd.Series

    total_trades = len(returns)
    win_rate = (returns > 0).mean() # returns > 0 gives T/F & python converts it to 1/0
    average_return = returns.mean()
    median_return = returns.median()
    equity_curve = (1 + returns).cumprod()
    cumulative_return = equity_curve.iloc[-1] - 1

    if returns.std(ddof=1) == 0:
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = (returns.mean() / returns.std(ddof=1)) * np.sqrt(total_trades)

    max_drawdown = compute_max_drawdown(equity_curve)

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "average_return": average_return,
        "median_return": median_return,
        "cumulative_return": cumulative_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown
    }

def main():
    trades_path = PROCESSED_DIR / "trades.csv"
    trades_df = pd.read_csv(trades_path)

    metrics = evaluate_trades(trades_df)
    metrics_df = pd.DataFrame([metrics])

    for col in ["win_rate",
                "average_return",
                "median_return",
                "cumulative_return",
                "sharpe_ratio",
                "max_drawdown"]:
        if col in metrics_df.columns:
            metrics_df[col] = metrics_df[col].round(4)

    output_path = PROCESSED_DIR / "metrics.csv"
    metrics_df.to_csv(output_path, index=False)

    print("\nBacktest Metrics:")
    print(metrics_df.to_string(index=False))

    print("\nSaved metrics to:")
    print(output_path)

if __name__ == "__main__":
    main()