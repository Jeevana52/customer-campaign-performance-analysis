SELECT job,
       COUNT(*) AS total_customers,
       SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END) AS responded,
       ROUND(
           SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2
       ) AS response_rate
FROM bank
GROUP BY job
ORDER BY response_rate DESC;