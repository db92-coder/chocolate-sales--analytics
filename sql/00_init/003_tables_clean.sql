DROP TABLE IF EXISTS clean.fact_chocolate_sales;

CREATE TABLE clean.fact_chocolate_sales (
  sales_person   TEXT NOT NULL,
  country        TEXT NOT NULL,
  product        TEXT NOT NULL,
  sale_date      DATE NOT NULL,
  amount         NUMERIC(12,2) NOT NULL,
  boxes_shipped  INTEGER NOT NULL,
  sale_date_raw  TEXT,
  amount_raw     TEXT
);
