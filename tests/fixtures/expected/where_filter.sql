SELECT COUNT(*) AS count, user
FROM app_logs
WHERE ((index = 'app_logs')) AND ((count > 100))
GROUP BY user;
