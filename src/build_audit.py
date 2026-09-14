"""
Runs the full cleaning pipeline (users + posts) and writes
audit/cleaning_summary.json from the real output — no numbers in this
file are hand-typed; they are computed from the cleaned dataframes.
"""
import json
from pathlib import Path

import pandas as pd

from clean_users import clean_users
from clean_posts import clean_posts

ROOT = Path(__file__).resolve().parents[1]


def main():
    users_df, users_audit = clean_users()
    posts_df, posts_audit = clean_posts()

    posts_df["timestamp"] = pd.to_datetime(posts_df["timestamp"])
    platform_summary = (
        posts_df.groupby("platform")["total_engagement"]
        .agg(posts="count", avg_total_engagement="mean", median_total_engagement="median")
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )
    monthly = (
        posts_df.assign(month=posts_df["timestamp"].dt.tz_localize(None).dt.to_period("M").astype(str))
        .groupby("month")
        .size()
        .to_dict()
    )

    markers = ["<div>", "<br>", "&amp;", "Ã©"]
    residual = {m: int(posts_df["text_content"].str.contains(m, regex=False, na=False).sum()) for m in markers}

    summary = {
        "source": "https://datavortex-social-engine.vercel.app/assets/index-B2FT5USN.js",
        "generated_by": "src/build_audit.py (runs src/clean_users.py + src/clean_posts.py)",
        "users": {
            "raw_rows": users_audit["raw_rows"],
            "clean_rows": users_audit["clean_rows"],
            "removed_missing_or_duplicate_id": users_audit["removed_missing_user_id"] + users_audit["removed_duplicate_user_id"],
            "follower_count_median_used": users_audit["follower_count_median_used"],
            "follower_count_imputed": users_audit["follower_count_imputed"],
            "invalid_account_created_dates": users_audit["invalid_account_created_dates"],
        },
        "posts": {
            "raw_rows": posts_audit["raw_rows"],
            "clean_rows": posts_audit["clean_rows"],
            "removed_missing_or_invalid": posts_audit["removed_missing_or_invalid"],
            "removed_duplicates": posts_audit["removed_duplicates"],
            "removed_total": posts_audit["removed_total"],
            "imputed_engagement": {
                "likes": posts_audit["likes_imputed"],
                "shares": posts_audit["shares_imputed"],
                "comments": posts_audit["comments_imputed"],
            },
            "platform_median_likes_used_for_imputation": posts_audit["platform_median_likes"],
            "engagement_outliers_flagged": posts_audit["engagement_outliers_flagged"],
            "engagement_iqr_upper_fence": posts_audit["engagement_iqr_upper_fence"],
        },
        "platform_summary": platform_summary,
        "monthly_post_volume": monthly,
        "residual_text_artifacts_in_cleaned_posts": residual,
        "residual_text_artifacts_preserved": True,
        "residual_text_artifact_decision": (
            "Detected during cleaning and retained because the documented cleaning "
            "methodology does not specify HTML/entity or character-encoding "
            "normalization as a record-removal criterion."
        ),
        "validation": {
            "cleaned_users_duplicate_user_ids": int(users_df["user_id"].duplicated().sum()),
            "cleaned_posts_duplicate_post_ids": int(posts_df["post_id"].duplicated().sum()),
            "cleaned_posts_missing_values_total": int(posts_df.isna().sum().sum()),
            "cleaned_posts_negative_likes": int((posts_df["likes"] < 0).sum()),
            "cleaned_posts_negative_shares": int((posts_df["shares"] < 0).sum()),
            "cleaned_posts_negative_comments": int((posts_df["comments"] < 0).sum()),
            "engagement_calculation_mismatches": int(
                (posts_df["total_engagement"] != posts_df["likes"] + posts_df["shares"] + posts_df["comments"]).sum()
            ),
        },
    }

    out_path = ROOT / "audit" / "cleaning_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
