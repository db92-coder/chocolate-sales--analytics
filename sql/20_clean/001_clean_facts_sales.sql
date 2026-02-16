TRUNCATE TABLE clean.fact_chocolate_sales;

INSERT INTO clean.fact_chocolate_sales (
  sales_person,
  country,
  product,
  sale_date,
  amount,
  boxes_shipped,
  sale_date_raw,
  amount_raw
)
SELECT
  trim(sales_person) AS sales_person,
  trim(country) AS country,
  trim(product) AS product,

  -- CSV date is DD/MM/YYYY
  to_date(trim(sale_date_raw), 'DD/MM/YYYY') AS sale_date,

  -- Amount like $5,320.00
  CAST(
    replace(
      replace(trim(amount_raw), '$', ''),
      ',',
      ''
    ) AS numeric(12,2)
  ) AS amount,

  -- Already numeric, no trim needed
  CAST(boxes_shipped_raw AS integer) AS boxes_shipped,

  sale_date_raw,
  amount_raw
FROM raw.chocolate_sales;
