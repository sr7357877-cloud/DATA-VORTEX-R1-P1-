# DATA VORTEX — Round 1 Phase 1
## Rebuilding the Social Engine

This repository contains the Dataset 01 cleaning pipeline and EDA deliverables for Round 1 Phase 1.

**GitHub repository:** _add your repo URL here after pushing_

## Rulebook-aligned deliverables

- Cleaned user dataset (CSV)
- Cleaned post dataset (CSV)
- EDA report
- Cleaning code (`src/clean_users.py`, `src/clean_posts.py`) — the actual pipeline that transforms the raw files into the cleaned deliverables
- Machine-readable cleaning audit, generated directly from the cleaning code (`src/build_audit.py`)
- A single notebook (`notebooks/Cleaning_and_Validation.ipynb`) that runs cleaning → audit → validation end to end
- Documented reproducibility/validation workflow

The rulebook requires cleaning code, documentation, and a reproducible workflow, and states that all transformations must be justified and assumptions clearly explained. Every number reported in `reports/EDA_Report.md` and `audit/cleaning_summary.json` is produced by running the code in `src/` on the raw files in `data/raw/` — nothing is hand-typed.

## Repository structure

```text
DATA_VORTEX_R1_P1_FINAL/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   └── cleaned/
├── src/
│   ├── clean_users.py        # raw users -> cleaned users
│   ├── clean_posts.py        # raw posts -> cleaned posts
│   ├── build_audit.py        # runs both + writes audit/cleaning_summary.json
│   └── validate_submission.py # checks the final artifacts (does not modify data)
├── reports/
│   └── EDA_Report.md
├── audit/
│   └── cleaning_summary.json
└── notebooks/
    └── Cleaning_and_Validation.ipynb
```

## How to reproduce everything from scratch

From the repository root:

```bash
pip install -r requirements.txt
python src/clean_users.py          # writes data/cleaned/Social_Engine_Users_Cleaned.csv
python src/clean_posts.py          # writes data/cleaned/Social_Engine_Posts_Cleaned.csv
python src/build_audit.py          # writes audit/cleaning_summary.json from the cleaned data
python src/validate_submission.py  # checks the results; does not modify anything
```

Or open `notebooks/Cleaning_and_Validation.ipynb` and run all cells, which does the same four steps in order.

## Final dataset counts

| Dataset | Raw | Clean | Removed |
|---|---:|---:|---:|
| Users | 1,500 | 1,500 | 0 |
| Posts | 12,360 | 8,737 | 3,623 |

The cleaning audit records 1,680 likes imputations (missing or negative values, per-platform median) and no shares/comments imputations. See `reports/EDA_Report.md` for the full methodology.

## Residual text artifacts

The final cleaned post dataset retains documented residual text artifacts (`<div>`, `<br>`, `&amp;`, and `Ã©`). They were detected during cleaning and preserved rather than silently altered because the documented cleaning methodology treats structural completeness — not HTML/entity or character-encoding normalization — as the removal criterion. Counts are recorded in `audit/cleaning_summary.json` and `reports/EDA_Report.md`.

## Assumptions and limitations

See `reports/EDA_Report.md` for the full documented cleaning methodology, assumptions, residual anomalies, EDA findings, and limitations.
