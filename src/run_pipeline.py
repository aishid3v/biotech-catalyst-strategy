from src.universe import load_universe

if __name__ == "__main__":
    df = load_universe()
    print (df.head())
    print("\nTickers:", df["ticker"].tolist())