#!/usr/bin/env python3
"""Final submission validation for DATA VORTEX Round 1 Phase 1.

Run AFTER clean_users.py and clean_posts.py (or build_audit.py, which runs
both). This script only validates the resulting cleaned files and audit
JSON — it does not clean or modify any data itself.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
AUDIT = ROOT / "audit" / "cleaning_summary.json"

users = pd.read_csv(CLEAN / "Social_Engine_Users_Cleaned.csv")
posts = pd.read_csv(CLEAN / "Social_Engine_Posts_Cleaned.csv")
raw_users = pd.read_csv(RAW / "Social_Engine_Users.csv")
raw_posts = pd.read_csv(RAW / "Social_Engine_Posts_Corrupted.csv")
audit = json.loads(AUDIT.read_text(encoding="utf-8"))

checks = {
    "raw_users_rows_match_source_file": len(raw_users) == audit["users"]["raw_rows"],
    "clean_users_rows_match_audit": len(users) == audit["users"]["clean_rows"],
    "clean_users_unique_ids": users["user_id"].is_unique,
    "raw_posts_rows_match_source_file": len(raw_posts) == audit["posts"]["raw_rows"],
    "clean_posts_rows_match_audit": len(posts) == audit["posts"]["clean_rows"],
    "clean_posts_unique_ids": posts["post_id"].is_unique,
    "clean_posts_no_missing": int(posts.isna().sum().sum()) == 0,
    "clean_posts_no_negative_likes": int(pd.to_numeric(posts["likes"], errors="coerce").lt(0).sum()) == 0,
    "clean_posts_no_negative_shares": int(pd.to_numeric(posts["shares"], errors="coerce").lt(0).sum()) == 0,
    "clean_posts_no_negative_comments": int(pd.to_numeric(posts["comments"], errors="coerce").lt(0).sum()) == 0,
    "engagement_consistent": int(
        (posts["total_engagement"] != posts["likes"] + posts["shares"] + posts["comments"]).sum()
    ) == 0,
    "likes_imputation_matches_audit": int(posts["likes_imputed"].sum()) == audit["posts"]["imputed_engagement"]["likes"],
    "shares_imputation_matches_audit": int(posts["shares_imputed"].sum()) == audit["posts"]["imputed_engagement"]["shares"],
    "comments_imputation_matches_audit": int(posts["comments_imputed"].sum()) == audit["posts"]["imputed_engagement"]["comments"],
}

for name, ok in checks.items():
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {name}")

if not all(checks.values()):
    raise SystemExit("Validation failed.")
print("All final submission checks passed.")
