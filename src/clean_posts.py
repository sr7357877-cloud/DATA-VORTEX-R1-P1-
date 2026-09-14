"""
DATA VORTEX — Round 1 Phase 1
Cleaning pipeline: Posts dataset

Rules implemented (documented in reports/EDA_Report.md):
  1. Trim whitespace on text fields; null-like strings ("null", "none",
     "nan", "n/a", "") are treated as missing.
  2. Platform labels are standardised to lowercase.
  3. Timestamps are accepted in three raw formats — DD-MM-YYYY, Unix epoch
     seconds, and ISO 8601 — and normalised to ISO 8601 at midnight UTC.
  4. A post is structurally invalid (and excluded) if it is missing a
     usable post_id, a user_id that exists in the cleaned users table,
     a platform, non-empty text content, or a parseable timestamp.
  5. Duplicate post_ids (after step 4) keep the most complete remaining
     row; ties keep the first occurrence.
  6. Likes: missing or negative values are treated as invalid and imputed
     with the per-platform median of valid (non-negative, non-missing)
     likes among the cleaned rows. Flagged in `likes_imputed`.
  7. Shares/comments: validated as non-negative; the raw data contained no
     negative or missing values for these fields, so `shares_imputed` and
     `comments_imputed` are always False but are retained for schema
     consistency with the audit/report.
  8. `total_engagement` = likes + shares + comments.
  9. `engagement_outlier` is flagged using an IQR rule on total_engagement:
     True if total_engagement > Q3 + 1.5 * IQR.
"""
from pathlib import Path
import html
import re
import pandas as pd
import numpy as np

RAW_POSTS = Path(__file__).resolve().parents[1] / "data" / "raw" / "Social_Engine_Posts_Corrupted.csv"
RAW_USERS = Path(__file__).resolve().parents[1] / "data" / "raw" / "Social_Engine_Users.csv"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "cleaned" / "Social_Engine_Posts_Cleaned.csv"
CLEANED_USERS = Path(__file__).resolve().parents[1] / "data" / "cleaned" / "Social_Engine_Users_Cleaned.csv"

NULL_LIKE_STRINGS = {"", "nan", "none", "null", "n/a", "na"}


def _clean_text(series: pd.Series) -> pd.Series:
    def clean_value(value):
        if pd.isna(value):
            return None

        value = str(value).strip()

        if value.lower() in NULL_LIKE_STRINGS:
            return None

        value = html.unescape(value)
        value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"</?div[^>]*>", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\s+", " ", value).strip()

        return value if value else None

    return series.map(clean_value)


def _parse_timestamp(raw: str):
    if raw is None:
        return pd.NaT
    raw = str(raw).strip()
    try:
        if raw.isdigit():
            return pd.to_datetime(int(raw), unit="s", utc=True).normalize()
        if len(raw) == 10 and raw.count("-") == 2 and raw.split("-")[0].isdigit() and len(raw.split("-")[0]) == 2:
            return pd.to_datetime(raw, format="%d-%m-%Y", utc=True).normalize()
        return pd.to_datetime(raw, utc=True).normalize()
    except (ValueError, TypeError):
        return pd.NaT


def clean_posts(raw_posts_path: Path = RAW_POSTS, raw_users_path: Path = RAW_USERS) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(raw_posts_path)
    raw_rows = len(raw)
    if not CLEANED_USERS.exists():
        raise FileNotFoundError(
            f"Cleaned users file not found: {CLEANED_USERS}. "
            "Run clean_users.py first."
        )

    valid_user_ids = set(
        pd.read_csv(CLEANED_USERS)["user_id"]
        .astype(str)
        .str.strip()
    )
    df = raw.copy()
    df["post_id"] = _clean_text(df["post_id"])
    df["user_id"] = _clean_text(df["user_id"])
    df["platform"] = _clean_text(df["platform"]).str.lower()
    df["text_content"] = _clean_text(df["text_content"])
    df["timestamp_parsed"] = df["timestamp"].map(_parse_timestamp)

    # Step 4: structural validity
    structurally_valid = (
        df["post_id"].notna()
        & df["user_id"].notna()
        & df["user_id"].isin(valid_user_ids)
        & df["platform"].notna()
        & df["text_content"].notna()
        & df["timestamp_parsed"].notna()
    )
    removed_missing_or_invalid = int((~structurally_valid).sum())
    df = df[structurally_valid].copy()

    # Step 5: de-duplicate on post_id, keep most complete row
    df["_completeness"] = df.notna().sum(axis=1)
    df = df.sort_values(["post_id", "_completeness"], ascending=[True, False])
    dup_mask = df["post_id"].duplicated(keep="first")
    removed_duplicates = int(dup_mask.sum())
    df = df[~dup_mask].drop(columns="_completeness")

    # Step 6: likes cleaning + per-platform median imputation
    likes = pd.to_numeric(df["likes"], errors="coerce")
    likes_invalid = likes.isna() | (likes < 0)
    df["likes_imputed"] = likes_invalid.values
    platform_median_likes = likes[~likes_invalid].groupby(df.loc[~likes_invalid, "platform"]).median()
    imputed_values = df.loc[likes_invalid, "platform"].map(platform_median_likes).round()
    likes = likes.where(~likes_invalid, imputed_values)
    df["likes"] = likes.round().astype(int)

    # Step 7: shares/comments validation
    shares = pd.to_numeric(df["shares"], errors="coerce")
    comments = pd.to_numeric(df["comments"], errors="coerce")

    if (shares.isna() | (shares < 0)).any():
        raise ValueError("Invalid shares values found.")

    if (comments.isna() | (comments < 0)).any():
        raise ValueError("Invalid comments values found.")

    df["shares"] = shares.astype(int)
    df["comments"] = comments.astype(int)

    df["shares_imputed"] = False
    df["comments_imputed"] = False
    # Step 8: total engagement
    df["total_engagement"] = df["likes"] + df["shares"] + df["comments"]

    # Step 9: IQR-based outlier flag
    q1, q3 = df["total_engagement"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    df["engagement_outlier"] = df["total_engagement"] > upper_fence

    # Final ISO timestamp string
    df["timestamp"] = df["timestamp_parsed"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df = df.drop(columns="timestamp_parsed")

    df = df.sort_values(["timestamp", "post_id"]).reset_index(drop=True)
    df = df[
        [
            "post_id", "user_id", "platform", "text_content", "timestamp",
            "likes", "likes_imputed", "shares", "shares_imputed",
            "comments", "comments_imputed", "total_engagement", "engagement_outlier",
        ]
    ]

    audit = {
        "raw_rows": raw_rows,
        "clean_rows": len(df),
        "removed_missing_or_invalid": removed_missing_or_invalid,
        "removed_duplicates": removed_duplicates,
        "removed_total": removed_missing_or_invalid + removed_duplicates,
        "likes_imputed": int(df["likes_imputed"].sum()),
        "shares_imputed": int(df["shares_imputed"].sum()),
        "comments_imputed": int(df["comments_imputed"].sum()),
        "engagement_outliers_flagged": int(df["engagement_outlier"].sum()),
        "engagement_iqr_upper_fence": round(float(upper_fence), 2),
        "platform_median_likes": {k: float(v) for k, v in platform_median_likes.items()},
    }
    return df, audit


if __name__ == "__main__":
    cleaned, audit = clean_posts()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUT_PATH, index=False)
    print("Posts cleaning complete.")
    for k, v in audit.items():
        print(f"  {k}: {v}")
