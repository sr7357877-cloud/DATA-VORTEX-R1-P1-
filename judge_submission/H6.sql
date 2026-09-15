WITH user_metrics AS (
    SELECT
        u.user_id,
        u.location,
        u.follower_count,
        COUNT(p.post_id) AS post_count,
        AVG(p.likes + p.shares + p.comments) AS avg_engagement,
        SUM(p.likes + p.shares + p.comments) AS total_engagement,
        MAX(CASE WHEN p.shares > p.likes THEN 1 ELSE 0 END) AS has_share_gt_like
    FROM users u
    JOIN posts p
        ON u.user_id = p.user_id
    GROUP BY u.user_id, u.location, u.follower_count
),
overall AS (
    SELECT AVG(likes + shares + comments) AS overall_avg_engagement
    FROM posts
)
SELECT
    user_metrics.user_id,
    user_metrics.location,
    user_metrics.follower_count,
    user_metrics.post_count,
    ROUND(user_metrics.avg_engagement, 2) AS avg_engagement,
    user_metrics.total_engagement
FROM user_metrics
CROSS JOIN overall
WHERE user_metrics.follower_count < 10000
  AND user_metrics.avg_engagement > overall.overall_avg_engagement
  AND user_metrics.has_share_gt_like = 1
ORDER BY user_metrics.total_engagement DESC;
