SELECT COUNT(*) AS count, SUM(price) AS total_revenue, AVG(duration), category, region
FROM sales
WHERE (index = 'sales')
GROUP BY category, region;
