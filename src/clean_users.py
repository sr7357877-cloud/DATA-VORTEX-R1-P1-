"""
DATA VORTEX — Round 1 Phase 1
Cleaning pipeline: Users dataset

Rules implemented (documented in reports/EDA_Report.md):
  1. Trim whitespace on text fields; standardise language codes to lowercase.
  2. Normalise `account_created` to ISO YYYY-MM-DD.
  3. Missing or negative follower counts are imputed with the overall median
     follower count and flagged in `follower_count_imputed`.
  4. Rows missing a usable `user_id` are dropped; duplicate `user_id`s keep
     the first occurrence.
"""
from pathlib import Path
import pandas as pd

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "Social_Engine_Users.csv"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "cleaned" / "Social_Engine_Users_Cleaned.csv"


def clean_users(raw_path: Path = RAW_PATH) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(raw_path)
    raw_rows = len(raw)

    df = raw.copy()

    # 1. Trim whitespace / normalise text fields
    for col in ["user_id", "location", "language"]:
        df[col] = df[col].astype(str).str.strip()
    df["language"] = df["language"].str.lower()

    # 2. Drop rows with missing/blank user_id
    df["user_id"] = df["user_id"].replace({"": None, "nan": None, "none": None, "null": None})
    missing_id_mask = df["user_id"].isna()
    removed_missing_id = int(missing_id_mask.sum())
    df = df[~missing_id_mask]

    # Drop duplicate user_ids, keep first occurrence
    dup_mask = df["user_id"].duplicated(keep="first")
    removed_duplicates = int(dup_mask.sum())
    df = df[~dup_mask]

    # 3. Normalise account_created to ISO date
    df["account_created"] = pd.to_datetime(df["account_created"], errors="coerce").dt.strftime("%Y-%m-%d")
    invalid_dates = int(df["account_created"].isna().sum())

    # 4. Impute missing/negative follower_count with median
    follower_count = pd.to_numeric(df["follower_count"], errors="coerce")
    invalid_follower = follower_count.isna() | (follower_count < 0)
    median_followers = int(round(follower_count[~invalid_follower].median()))
    df["follower_count_imputed"] = invalid_follower.values
    follower_count = follower_count.where(~invalid_follower, median_followers)
    df["follower_count"] = follower_count.astype(int)

    df = df.sort_values("user_id").reset_index(drop=True)

    audit = {
        "raw_rows": raw_rows,
        "clean_rows": len(df),
        "removed_missing_user_id": removed_missing_id,
        "removed_duplicate_user_id": removed_duplicates,
        "invalid_account_created_dates": invalid_dates,
        "follower_count_median_used": median_followers,
        "follower_count_imputed": int(df["follower_count_imputed"].sum()),
    }
    return df, audit


if __name__ == "__main__":
    cleaned, audit = clean_users()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUT_PATH, index=False)
    print("Users cleaning complete.")
    for k, v in audit.items():
        print(f"  {k}: {v}")
