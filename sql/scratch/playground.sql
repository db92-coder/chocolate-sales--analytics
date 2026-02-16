SELECT
    month,
    country,
    product,
    total_sales_amount,
    mom_growth_sales,
    opportunity_rank
FROM marts.opportunity_scores
ORDER BY month DESC, opportunity_rank ASC
LIMIT 10;
