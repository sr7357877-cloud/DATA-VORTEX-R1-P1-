# Social Engine Dataset 01: Cleaning and EDA Report

## Deliverables

- `Social_Engine_Users_Cleaned.csv`: 1,500 cleaned user records.
- `Social_Engine_Posts_Cleaned.csv`: 8,712 cleaned post records.
- `cleaning_summary.json`: machine-readable cleaning log and summary metrics, generated directly by `src/build_audit.py`.

All figures in this report are generated from the current cleaning pipeline and audit output. Re-running the pipeline reproduces the reported cleaning and validation metrics.

## Cleaning method

The source data was recovered from the Dataset 01 files exposed by the Social Engine site. User IDs and post IDs were treated as unique identifiers. Whitespace was trimmed on text fields, null-like values (`NULL`, `None`, `N/A`, and blank fields) were converted to missing values, and platform labels were standardised to lowercase.

Post timestamps were accepted in three raw formats — `DD-MM-YYYY`, Unix epoch seconds, and ISO 8601 — and normalised to UTC midnight. Posts missing a usable post ID, a user ID that exists in the cleaned users table, a platform, non-empty text, or a parseable timestamp were excluded as structurally invalid. Among the remaining valid rows, duplicate post IDs were resolved by keeping the most complete remaining row for that ID.

Likes were treated as invalid if missing or negative and were imputed using the per-platform median of valid likes. The imputation is disclosed per-row in `likes_imputed`. Shares and comments were validated as non-negative. No invalid shares or comments required imputation.

Engagement was not winsorised or deleted. `total_engagement` is the sum of likes, shares, and comments. `engagement_outlier` flags rows where `total_engagement` exceeds the IQR upper fence (Q3 + 1.5×IQR), calculated from the cleaned data.

## Data quality results

| Measure | Users | Posts |
| --- | ---: | ---: |
| Raw records | 1,500 | 12,360 |
| Clean records | 1,500 | 8,712 |
| Removed — structurally invalid | 0 | 3,400 |
| Removed — duplicate post_id | 0 | 248 |
| Total removed | 0 | 3,648 |

The 3,400 structurally invalid post records were excluded because they failed one or more required structural checks. Duplicate post IDs were then resolved by retaining the most complete valid record.

Of the 8,712 cleaned posts, 1,673 had missing or negative likes values and received platform-level median imputation.

Platform medians used for likes imputation were:

| Platform | Median likes |
| --- | ---: |
| Facebook | 2,571.0 |
| Instagram | 2,493.5 |
| Reddit | 2,471.0 |
| Twitter | 2,417.0 |
| YouTube | 2,525.0 |

No shares or comments values required imputation.

## Residual text artifacts

HTML and HTML-entity artifacts were cleaned from the post text during processing. The current audit reports zero remaining occurrences of `<div>`, `<br>`, and `&amp;`.

One character-encoding artifact, `Ã©`, remains in 261 cleaned records. These records were retained because the current cleaning methodology does not remove otherwise structurally valid records solely because of character-encoding anomalies.

| Artifact | Records in cleaned posts |
| --- | ---: |
| `<div>` | 0 |
| `<br>` | 0 |
| `&amp;` | 0 |
| `Ã©` | 261 |

This limitation should be considered if the dataset is later used for detailed text or language analysis.

## Exploratory findings

### Post volume

The cleaned post dataset covers **1 May 2024 through 30 April 2025**.

| Month | Posts |
| --- | ---: |
| May 2024 | 761 |
| June 2024 | 713 |
| July 2024 | 743 |
| August 2024 | 731 |
| September 2024 | 689 |
| October 2024 | 744 |
| November 2024 | 741 |
| December 2024 | 746 |
| January 2025 | 712 |
| February 2025 | 667 |
| March 2025 | 741 |
| April 2025 | 724 |

May 2024 had the highest post volume with 761 posts, while February 2025 had the lowest with 667.

### Platform distribution and engagement

| Platform | Posts | Avg. total engagement | Median total engagement |
| --- | ---: | ---: | ---: |
| Facebook | 1,772 | 4,033.13 | 4,050 |
| Instagram | 1,697 | 4,038.52 | 3,990 |
| Reddit | 1,719 | 3,955.70 | 3,957 |
| Twitter | 1,747 | 3,939.95 | 3,906 |
| YouTube | 1,777 | 4,019.38 | 4,048 |

Instagram has the highest average total engagement at 4,038.52, while Twitter has the lowest at 3,939.95. The relatively small difference suggests that platform alone does not explain most engagement variation in this recovered dataset.

### Engagement distribution

Across all 8,712 cleaned posts:

- Mean total engagement: **3,997.41**
- Median total engagement: **3,994**
- Minimum: **153**
- Maximum: **7,893**
- IQR upper fence: **8,039**
- Engagement outliers flagged: **0**

No cleaned post exceeds the calculated IQR upper fence.

### User data

The cleaned user dataset contains 1,500 users.

Follower counts range from **109 to 49,944**, with a median of **24,742**. No follower-count imputation was required.

The most frequent user languages are:

- Chinese (`zh`): 168 users
- Hindi (`hi`): 156 users
- Japanese (`ja`): 156 users
- English (`en`): 153 users
- French (`fr`): 150 users

## Validation

The final cleaned datasets were checked for:

- Duplicate user IDs
- Duplicate post IDs
- Missing cleaned post values
- Negative likes, shares, and comments
- Incorrect engagement calculations
- Imputation-flag consistency

The current audit reports zero duplicate post IDs, zero missing cleaned-post values, zero negative engagement components, and zero engagement-calculation mismatches.

## Reproducibility and limitations

The cleaning method is implemented in `src/clean_users.py` and `src/clean_posts.py`. The process is orchestrated by `src/build_audit.py`, which generates `audit/cleaning_summary.json` directly from the current cleaned data.

The repository preserves the raw source files separately from the cleaned deliverables.

The cleaned post dataset retains imputation flags so downstream analysis can distinguish original values from imputed likes.

The remaining `Ã©` character-encoding artifact should be considered a limitation for downstream text analysis. It does not affect the structural or numerical validation of the cleaned dataset.