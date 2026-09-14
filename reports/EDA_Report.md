# Social Engine Dataset 01: Cleaning and EDA Report

## Deliverables

- `Social_Engine_Users_Cleaned.csv`: 1,500 cleaned user records.
- `Social_Engine_Posts_Cleaned.csv`: 8,737 cleaned post records.
- `cleaning_summary.json`: machine-readable cleaning log and summary metrics, generated directly by `src/build_audit.py`.

All figures in this report are produced by running `src/clean_users.py` and `src/clean_posts.py` on the raw files in `data/raw/` — none are hand-entered. Re-running the pipeline (`python src/build_audit.py`, or `notebooks/Cleaning_and_Validation.ipynb`) reproduces every number below.

## Cleaning method

The source data was recovered from the Dataset 01 files exposed by the corrupted Social Engine site. User IDs and post IDs were treated as unique identifiers. Whitespace was trimmed on text fields, null-like values (`NULL`, `None`, `N/A`, and blank fields) were converted to missing values, and platform and language labels were standardised to lowercase.

Post timestamps were accepted in three raw formats — `DD-MM-YYYY`, Unix epoch seconds, and ISO 8601 — and normalised to ISO 8601 at midnight UTC. Posts missing a usable post ID, a user ID that exists in the cleaned users table, a platform, non-empty text, or a parseable timestamp were excluded as structurally invalid. Among the remaining valid rows, duplicate post IDs were resolved by keeping the most complete remaining row for that ID.

Likes were treated as invalid if missing **or negative** (a negative like count is not a valid observation), and were imputed with the per-platform median of valid likes among the cleaned rows; the imputation is disclosed per-row in `likes_imputed`. Shares and comments were validated as non-negative; the raw data contained no negative or missing values for these two fields, so no imputation was required (`shares_imputed` / `comments_imputed` are retained as columns for schema consistency but are always `False`).

Engagement was not winsorised or deleted. `total_engagement` is the sum of likes, shares, and comments; `engagement_outlier` flags rows where `total_engagement` exceeds the IQR upper fence (Q3 + 1.5×IQR), computed from the cleaned data.

## Data quality results

| Measure | Users | Posts |
| --- | ---: | ---: |
| Raw records | 1,500 | 12,360 |
| Clean records | 1,500 | 8,737 |
| Removed — structurally invalid (missing platform/text/timestamp/valid user) | 0 | 3,374 |
| Removed — duplicate post_id (kept most complete row) | 0 | 249 |
| Total removed | 0 | 3,623 |

Of the 3,374 structural exclusions, the dominant causes are missing platform labels and missing/null-like text content in the raw source. The raw post file contains 12,360 rows and 12,000 unique post IDs (360 rows are excess copies of an already-seen post_id); after structural filtering, 249 of the remaining rows were still duplicates of an ID already present and were dropped in favor of the most complete version of that record.

8,737 clean posts remain. Of these, 1,680 had a missing or negative likes value; those values were imputed using each platform's median likes (facebook 2,571; instagram 2,492; reddit 2,472; twitter 2,433.5; youtube 2,526). No user follower counts required imputation — the raw users file contained no missing or negative follower counts.

## Residual text anomalies

Validation of the final cleaned post dataset identified several recurring text artifacts: HTML-like fragments (`<div>`, `<br>`), the HTML entity `&amp;`, and the encoding artifact `Ã©`. These affected records were retained because the documented cleaning methodology treats structural completeness (valid ID, platform, non-empty text, parseable timestamp) as the removal criterion, not HTML/entity decoding or character-encoding normalization. They are documented here as a residual data-quality limitation for downstream text analysis, not silently altered.

| Artifact | Records in cleaned posts |
| --- | ---: |
| `<div>` | 295 |
| `<br>` | 268 |
| `&amp;` | 269 |
| `Ã©` | 261 |

## Exploratory findings

- The cleaned post set covers 1 May 2024 through 30 April 2025. May 2024 has the highest volume (765 posts); February 2025 is the lowest (670).
- Engagement is fairly even across platforms: Instagram has the highest mean total engagement (4,036.85) and Twitter the lowest (3,946.79) — platform alone does not explain much variation in this recovered set.
- Median total engagement across cleaned posts is 3,994, ranging from 153 to 7,893. No record exceeded the IQR upper fence of 8,042.5, so no engagement outliers were flagged under this rule.
- The user base is geographically and linguistically diverse. The most frequent language is Chinese (`zh`, 168 users), followed by Hindi and Japanese (156 each), then English (153) and French (150).
- Follower counts range from 109 to 49,944, with a median of 24,741.5.

## Validation

`src/validate_submission.py` checks the final cleaned files for: row counts matching the audit, duplicate identifiers, missing values, negative engagement values, engagement-sum consistency, and imputation-flag consistency against `audit/cleaning_summary.json`. All checks currently pass — see the printed output when the script is run, or re-run it from the repository root:

```bash
pip install -r requirements.txt
python src/clean_users.py
python src/clean_posts.py
python src/build_audit.py
python src/validate_submission.py
```

## Reproducibility and limits

The cleaning method is implemented in `src/clean_users.py` and `src/clean_posts.py`, orchestrated end to end in `notebooks/Cleaning_and_Validation.ipynb`. The machine-readable audit is generated by `src/build_audit.py` directly from the cleaned dataframes — it is not a separately maintained or hand-edited file. The cleaned post file retains imputation flags so downstream analysis can exclude or separately test imputed engagement values. Values marked as missing or negative in the source are not assumed to mean zero; likes are median-imputed per platform, while incomplete structural records are excluded rather than guessed at.

The repository preserves the raw source files separately from the cleaned deliverables. Residual text artifacts are explicitly recorded rather than silently altered.
