DROP TABLE IF EXISTS marts.sales_by_month_country_product;

CREATE TABLE marts.sales_by_month_country_product AS
SELECT
  date_trunc('month', sale_date)::date AS month,
  country,
  product,
  SUM(amount) AS total_sales_amount,
  SUM(boxes_shipped) AS total_boxes,
  COUNT(*) AS transactions
FROM clean.fact_chocolate_sales
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
