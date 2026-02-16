DROP TABLE IF EXISTS marts.salesperson_performance;

CREATE TABLE marts.salesperson_performance AS
SELECT
  sales_person,
  country,
  SUM(amount) AS total_sales_amount,
  SUM(boxes_shipped) AS total_boxes,
  COUNT(*) AS transactions,
  ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2) AS avg_amount_per_box
FROM clean.fact_chocolate_sales
GROUP BY 1, 2
ORDER BY total_sales_amount DESC;
