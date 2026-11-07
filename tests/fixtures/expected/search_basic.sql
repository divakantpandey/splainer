SELECT COUNT(*) AS count, sourcetype
FROM main
WHERE (index = 'main')
GROUP BY sourcetype;
