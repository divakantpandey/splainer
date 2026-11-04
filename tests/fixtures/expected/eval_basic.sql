SELECT *, (duration / 1000) AS duration_seconds
FROM network
WHERE (index = 'network');
