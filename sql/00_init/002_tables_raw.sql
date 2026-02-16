DROP TABLE IF EXISTS raw.chocolate_sales;

CREATE TABLE raw.chocolate_sales (
  sales_person   TEXT,
  country        TEXT,
  product        TEXT,
  sale_date_raw  TEXT,
  amount_raw     TEXT,
  boxes_shipped_raw TEXT
);
