SELECT count AS total_requests, status_code AS HTTP_Status
FROM main
WHERE (index = 'main')
GROUP BY status_code
ORDER BY total_requests DESC;
