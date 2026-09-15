# Phase 2 Judge Submission

## Selected Questions

- Easy: E2 — Most Engaged Posts
- Medium: M1 — Engagement by Location
- Hard: H6 — Qualified High-Engagement Users

## Evidence

The `screenshots/` directory contains the actual SQL query output screenshots for the selected questions.

## Query Notes

### E2
Returns the top 10 posts by total engagement (likes + shares + comments).

The cleaned dataset stores originally missing likes using the `likes_imputed` flag. To follow the judge instruction to ignore posts where likes were missing, the query uses:

`WHERE likes_imputed = FALSE`

### M1
Joins the users and posts datasets, calculates total engagement by location, counts posts, and ranks locations by total engagement in descending order.

### H6
Returns users who satisfy all three required conditions:

1. Fewer than 10,000 followers.
2. Average post engagement above the overall average engagement.
3. At least one post where shares exceed likes.

Results are ranked by total engagement in descending order.
