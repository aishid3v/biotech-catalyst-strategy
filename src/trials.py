import pandas as pd
from pathlib import Path
from pytrials.client import ClinicalTrials
from src.universe import load_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

ct = ClinicalTrials()

def fetch_trials_for_company(search_terms: str, max_studies: int = 500): #fetches trials for one company
    studies = ct.get_study_fields(search_expr=search_terms,
                                  fields=["NCTId", "Phase", "OverallStatus", "PrimaryCompletionDate"],
                                  max_studies=max_studies, fmt="json")
    
    rows = studies.get("studies", [])
    print(f"Number of raw studies returned for {search_terms}: {len(rows)}")

    if not rows:
        return pd.DataFrame()
    
    cleaned = []

    for s in rows:
        protocol = s.get("protocolSection", {})

        nct_id = protocol.get("identificationModule", {}).get("nctId")
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})

        overall_status = status.get("overallStatus")

        primary_date = None

        if "primaryCompletionDateStruct" in status:
            primary_date = status["primaryCompletionDateStruct"].get("date")

        phases = design.get("phases", [])
        phase = phases[0] if phases else None

        cleaned.append({
            "NCTId": nct_id,
            "Phase": phase,
            "OverallStatus": overall_status,
            "PrimaryCompletionDate": primary_date
        })

    print(f"Number of cleaned studies for {search_terms}: {len(cleaned)}")

    df = pd.DataFrame(cleaned)

    if df.empty:
        return df

    df["Phase"] = df["Phase"].replace({
        "PHASE1": "Phase 1",
        "PHASE2": "Phase 2",
        "PHASE3": "Phase 3",
        "EARLY_PHASE1": "Early Phase 1"
    })

    df["PrimaryCompletionDate"] = pd.to_datetime(df["PrimaryCompletionDate"], errors="coerce")

    print(df.head())

    return df


def compute_pipeline_score(df: pd.DataFrame):
    phase_weights = {
        "Early Phase 1": 0.10,
        "Phase 1": 0.20,
        "Phase 2": 0.35,
        "Phase 3": 0.65
    } # probability of drug being eventually approved in each phase
    phase_counts = df["Phase"].value_counts()
    raw_score = 0.0

    for phase, weight in phase_weights.items():
        raw_score += phase_counts.get(phase, 0) * weight

    return round(raw_score, 4)


def build_pipeline_scores(trials_data: dict):
    pipeline_rows = []

    for ticker, df in trials_data.items():
        raw_score = compute_pipeline_score(df)

        pipeline_rows.append({"ticker": ticker, "raw score": raw_score})
        pipeline_df = pd.DataFrame(pipeline_rows)

        max_score = pipeline_df["raw_score"].max()

        if max_score == 0:
            pipeline_df["pipeline_score"] = 0 # creates new column
        else:
            pipeline_df["pipeline_score"] = (pipeline_df["raw_score"] / max_score)

        pipeline_df["pipeline_score"] = pipeline_df["pipeline_score"].round(3)

        return pipeline_df
    

def extract_catalysts(df: pd.DataFrame, start_year: int = 2020, end_year: int = 2025):
    out = df.copy()
    out = out[out["OverallStatus"] == "COMPLETED"] # where the catalyst has already happened
    out = out.dropna(subset=["PrimaryCompletionDate"])
    out = out[(out["PrimaryCompletionDate"].dt.year >= start_year) & (out["PrimaryCompletionDate"].dt.year <= end_year)]

    return out[["NCTId", "Phase", "PrimaryCompletionDate"]]


def run_trials_pipeline():
    universe = load_universe()

    pipeline_rows = []
    catalyst_rows = []

    for _, row in universe.iterrows():
        ticker = row["ticker"]
        search_terms = row["search_terms"]

        print(f"Fetching trials for {ticker}...")

        df = fetch_trials_for_company(search_terms)

        if df.empty:
            print(f"No trials found for {ticker}")
            continue

        score = compute_pipeline_score(df)

        pipeline_rows.append({"ticker": ticker, "pipeline_score": score})

        catalysts = extract_catalysts(df)
        for _, c in catalysts.iterrows():
            catalyst_rows.append(
                {
                    "ticker": ticker,
                    "nct_id": c["NCTId"],
                    "phase": c["Phase"],
                    "catalyst_date": c["PrimaryCompletionDate"]
                }
            )

    pipeline_df = pd.DataFrame(pipeline_rows)

    pipeline_df["pipeline_score"] = (pipeline_df["pipeline_score"].rank(pct=True)).round(3)

    catalysts_df = pd.DataFrame(catalyst_rows, columns=["ticker", "nct_id", "phase", "catalyst_date"])

    pipeline_df.to_csv(PROCESSED_DIR / "pipeline_scores.csv", index=False)
    catalysts_df.to_csv(PROCESSED_DIR / "catalysts.csv", index=False)

    print("pipeline_rows:", pipeline_rows[:5])
    print("catalyst_rows:", catalyst_rows[:5])
    print(f"Pipeline rows: {len(pipeline_rows)}")
    print(f"Catalyst rows: {len(catalyst_rows)}")

    print("\nSaved:")
    print(" - data/processed/pipeline_scores.csv")
    print(" - data/processed/catalysts.csv")

if __name__ == "__main__":
    run_trials_pipeline()