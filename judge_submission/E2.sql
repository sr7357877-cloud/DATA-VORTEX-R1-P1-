SELECT
    post_id,
    platform,
    likes,
    shares,
    comments,
    total_engagement
FROM posts
WHERE likes_imputed = FALSE
ORDER BY total_engagement DESC
LIMIT 10;
