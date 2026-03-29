import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universe.csv"

def load_universe(): # loads and cleans biotech universe data
    df = pd.read_csv(UNIVERSE_PATH)

    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["company_name"] = df["company_name"].astype(str).str.strip()
    df["search_terms"] = df["search_terms"].astype(str).str.strip()

    df = df[df["ticker"].notna() & (df["ticker"] != "")]
    df = df.drop_duplicates(subset=["ticker"]).reset_index(drop=True)

    return df