DROP TABLE IF EXISTS clean.customers_rejects;

CREATE TABLE clean.customers_rejects AS
SELECT
  customer_id,
  lower(trim(email)) AS email,
  country,
  created_at AS created_at_raw
FROM raw.customers
WHERE created_at IS NULL
   OR trim(created_at) = ''
   OR NOT (
     trim(created_at) ~ '^\d{4}-\d{2}-\d{2}$'
     OR trim(created_at) ~ '^\d{4}/\d{2}/\d{2}$'
     OR trim(created_at) ~ '^\d{2}-\d{2}-\d{4}$'
   );
