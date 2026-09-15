SELECT
    u.location,
    COUNT(p.post_id) AS post_count,
    SUM(p.likes + p.shares + p.comments) AS total_engagement,
    RANK() OVER (
        ORDER BY SUM(p.likes + p.shares + p.comments) DESC
    ) AS rank
FROM users u
JOIN posts p
    ON u.user_id = p.user_id
GROUP BY u.location
ORDER BY total_engagement DESC;
