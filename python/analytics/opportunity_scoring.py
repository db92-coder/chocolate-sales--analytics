print("START: opportunity_scoring.py")
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "practice")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

QUERY = """
SELECT
  sale_date,
  country,
  product,
  amount,
  boxes_shipped
FROM clean.fact_chocolate_sales
WHERE sale_date IS NOT NULL
"""

def zscore(series: pd.Series) -> pd.Series:
    # robust to constant series (avoid divide by zero)
    std = series.std(ddof=0)
    if std == 0 or np.isnan(std):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - series.mean()) / std

def minmax(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn or np.isnan(mx - mn):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - mn) / (mx - mn)

def main():
    df = pd.read_sql(QUERY, engine)

    # month bucket
    df["month"] = pd.to_datetime(df["sale_date"]).dt.to_period("M").dt.to_timestamp()

    # aggregate to month x country x product
    agg = (
        df.groupby(["month", "country", "product"], as_index=False)
          .agg(
              total_sales_amount=("amount", "sum"),
              total_boxes=("boxes_shipped", "sum"),
              transactions=("amount", "size"),
          )
          .sort_values(["country", "product", "month"])
    )

    # feature engineering per (country, product)
    g = agg.groupby(["country", "product"], group_keys=False)

    # previous month metrics
    agg["sales_prev_month"] = g["total_sales_amount"].shift(1)
    agg["boxes_prev_month"] = g["total_boxes"].shift(1)

    # # MoM growth (sales)
    # agg["mom_growth_sales"] = np.where(
    #     (agg["sales_prev_month"].isna()) | (agg["sales_prev_month"] <= 0),
    #     np.nan,
    #     (agg["total_sales_amount"] - agg["sales_prev_month"]) / agg["sales_prev_month"],
    # )

    # 3-month rolling features (trend + stability)
    agg["sales_roll3_mean"] = g["total_sales_amount"].transform(lambda s: s.rolling(3, min_periods=2).mean())
    agg["sales_roll3_std"]  = g["total_sales_amount"].transform(lambda s: s.rolling(3, min_periods=2).std(ddof=0))
    # agg["mom_growth_roll3_mean"] = g["mom_growth_sales"].transform(lambda s: s.rolling(3, min_periods=2).mean())

    # “momentum”: change over 3 months (current - 3 months ago)
    agg["sales_3m_ago"] = g["total_sales_amount"].shift(3)
    # agg["growth_3m"] = np.where(
    #     (agg["sales_3m_ago"].isna()) | (agg["sales_3m_ago"] <= 0),
    #     np.nan,
    #     (agg["total_sales_amount"] - agg["sales_3m_ago"]) / agg["sales_3m_ago"],
    # )
    # ---- LOG GROWTH ----

    # log current and previous (log1p handles zeros safely)
    agg["log_sales"] = np.log1p(agg["total_sales_amount"])
    agg["log_sales_prev_month"] = g["log_sales"].shift(1)

    # Log MoM growth
    agg["mom_growth_sales"] = agg["log_sales"] - agg["log_sales_prev_month"]

    # 3-month lag
    agg["log_sales_3m_ago"] = g["log_sales"].shift(3)

    # Log 3-month growth
    agg["growth_3m"] = agg["log_sales"] - agg["log_sales_3m_ago"]


    # ---- scoring ----
    # We score per month across all product-country combos.
    # Intuition:
    # - reward meaningful volume (sales)
    # - reward momentum (MoM / 3-month growth)
    # - penalise volatility (rolling std)
    # - require minimum activity to avoid “tiny base rate” traps

    scored = agg.copy()

    # basic filters to reduce noise (tweak any time)
    scored["meets_min_activity"] = (scored["transactions"] >= 2) & (scored["total_boxes"] >= 10)

    # normalised components per month (so scores are comparable within the month)
    scored["sales_norm"] = scored.groupby("month")["total_sales_amount"].transform(minmax)
    scored["mom_norm"]   = scored.groupby("month")["mom_growth_sales"].transform(lambda s: minmax(s.fillna(0)))
    scored["g3m_norm"]   = scored.groupby("month")["growth_3m"].transform(lambda s: minmax(s.fillna(0)))

    # volatility: higher std = worse (invert)
    scored["vol_norm_raw"] = scored.groupby("month")["sales_roll3_std"].transform(lambda s: minmax(s.fillna(0)))
    scored["stability_norm"] = 1 - scored["vol_norm_raw"]

    # weighted score (weights you can tune later)
    scored["opportunity_score"] = (
        0.45 * scored["sales_norm"] +
        0.25 * scored["mom_norm"] +
        0.20 * scored["g3m_norm"] +
        0.10 * scored["stability_norm"]
    )

    # apply penalty if not enough activity (keeps “false hot” combos from topping the list)
    scored.loc[~scored["meets_min_activity"], "opportunity_score"] *= 0.5

    # rank within each month (1 = best)
    scored["opportunity_rank"] = scored.groupby("month")["opportunity_score"].rank(ascending=False, method="dense").astype(int)

    # keep only columns we want in marts
    out = scored[[
        "month", "country", "product",
        "total_sales_amount", "total_boxes", "transactions",
        "mom_growth_sales", "growth_3m", "sales_roll3_std",
        "opportunity_score", "opportunity_rank", "meets_min_activity"
    ]].copy()

    # nice rounding
    out["opportunity_score"] = out["opportunity_score"].round(4)
    out["mom_growth_sales"] = out["mom_growth_sales"].round(4)
    out["growth_3m"] = out["growth_3m"].round(4)
    out["sales_roll3_std"] = out["sales_roll3_std"].round(2)

    # write to marts
    out.to_sql("opportunity_scores", engine, schema="marts", if_exists="replace", index=False)
    print("END: wrote opportunity_scores")


    print("Wrote marts.opportunity_scores rows:", len(out))
    print("Months:", out["month"].nunique(), "| Countries:", out["country"].nunique(), "| Products:", out["product"].nunique())

if __name__ == "__main__":
    main()
