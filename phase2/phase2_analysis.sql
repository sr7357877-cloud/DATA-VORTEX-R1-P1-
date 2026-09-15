-- Social Engine Phase 2 Analytical Core

-- Challenge 1: Trend Detection
SELECT strftime(timestamp, '%Y-%m') AS month, COUNT(*) AS post_count, ROUND(AVG(total_engagement), 2) AS avg_engagement FROM posts GROUP BY month ORDER BY month;

-- Challenge 2: Platform Engagement Analysis
SELECT platform, COUNT(*) AS post_count, ROUND(AVG(total_engagement), 2) AS avg_engagement, ROUND(MEDIAN(total_engagement), 2) AS median_engagement FROM posts GROUP BY platform ORDER BY avg_engagement DESC;

-- Challenge 3: High-Engagement Detection
WITH ranked AS (SELECT post_id, user_id, platform, total_engagement, ROW_NUMBER() OVER (PARTITION BY platform ORDER BY total_engagement DESC) AS rank_within_platform FROM posts) SELECT post_id, user_id, platform, total_engagement, rank_within_platform FROM ranked WHERE rank_within_platform <= 10 ORDER BY platform, rank_within_platform;

-- Challenge 4: Behavioural User Grouping
WITH user_stats AS (SELECT u.user_id, COUNT(p.post_id) AS post_count, ROUND(AVG(p.total_engagement), 2) AS avg_engagement FROM users u LEFT JOIN posts p ON u.user_id=p.user_id GROUP BY u.user_id), grouped AS (SELECT user_id, post_count, avg_engagement, CASE WHEN post_count >= 10 THEN 'Power User' WHEN post_count >= 5 THEN 'Active User' ELSE 'Casual User' END AS user_group FROM user_stats) SELECT user_group, COUNT(*) AS user_count, ROUND(AVG(post_count), 2) AS avg_posts, ROUND(AVG(avg_engagement), 2) AS avg_engagement FROM grouped GROUP BY user_group ORDER BY user_count DESC;

-- Challenge 5: Correlation Analysis
SELECT ROUND(corr(likes, shares), 4) AS likes_shares_corr, ROUND(corr(likes, comments), 4) AS likes_comments_corr, ROUND(corr(shares, comments), 4) AS shares_comments_corr FROM posts;
