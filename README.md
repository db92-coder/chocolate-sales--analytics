<div align="center">

# 🍫 Chocolate Sales Analytics Pipeline

**End-to-end analytics project**: PostgreSQL → SQL marts → Python modelling → Power BI dashboards  
Built to simulate a real-world analytics workflow (data modelling, feature engineering, scoring, and BI delivery).

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-yellow?logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboarding-F2C811?logo=powerbi&logoColor=black)
![Status](https://img.shields.io/badge/Status-Active-success)

</div>

---

## ✨ What this project does

This project turns raw chocolate sales data into **marketing decision intelligence**.

It produces a monthly ranked table: **`marts.opportunity_scores`**, which highlights the best **product–country** combinations to target with advertising based on:

- **Sales volume** (meaningful demand)
- **Momentum** (log-based MoM growth)
- **Sustained trend** (log-based 3-month growth)
- **Stability** (volatility penalty)
- **Minimum activity thresholds** (reduces noise)

---

## 🧱 Architecture

```text
Raw CSV
  ↓
PostgreSQL (raw schema)
  ↓
Clean layer (clean schema)
  ↓
Analytics marts (marts schema)
  ↓
Python feature engineering + scoring
  ↓
marts.opportunity_scores
  ↓
Power BI dashboards (Executive + Product + Sales Team + Marketing Opportunities)

🛠 Tech stack

PostgreSQL 16 (Docker)

SQL (data cleaning + marts)

Python (pandas, numpy, SQLAlchemy, python-dotenv)

Power BI (interactive dashboards)

VS Code + SQLTools

Git / GitHub


📁 Project structure
sql-lab/
├─ sql/
│  ├─ 10_schema/
│  ├─ 20_clean/
│  └─ 30_marts/
├─ python/
│  ├─ load/
│  └─ analytics/
├─ data/
│  └─ raw/        (not committed)
├─ .env.example
├─ requirements.txt
└─ README.md


🧠 Modelling approach
Feature engineering (monthly product × country)

For each month, product, country:

total_sales_amount

total_boxes

transactions

mom_growth_sales (log growth)

growth_3m (log growth)

sales_roll3_std (rolling volatility)

Log growth was chosen to stabilise extreme percentage growth caused by small base values.

Opportunity score

A weighted composite index (normalised per month):

45% Sales volume

25% Momentum (MoM log growth)

20% 3-month log growth

10% Stability (inverted volatility)

Lower opportunity_rank means higher priority (rank 1 is best).

🚀 Quickstart
1) Create environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\activate
pip install -r requirements.txt

2) Configure DB settings

Copy .env.example → .env and update values.

3) Run scoring pipeline
python python/analytics/opportunity_scoring.py

4) Validate in Postgres
SELECT COUNT(*) FROM marts.opportunity_scores;

SELECT *
FROM marts.opportunity_scores
ORDER BY month DESC, opportunity_rank ASC
LIMIT 10;

5) Refresh Power BI

Load marts.opportunity_scores and refresh visuals.

📊 Dashboard pages

Sales Overview — executive KPIs + trend + country breakdown

Product Analytics — top products, contribution, growth, trends

Sales Team Analytics — top performers, product mix, country focus

Marketing Opportunities — scatter matrix (growth vs volume, sized by score), Top 10 table, trend drilldown

<details> <summary><strong>✅ Real-world notes</strong> (click to expand)</summary>

Uses a layered modelling approach: raw → clean → marts

Scoring is built outside Power BI to simulate analytics engineering workflows

Growth is log-based to avoid base-rate distortions

Final outputs are written back into Postgres to create BI-ready marts

</details>
🔮 Future improvements

Year-over-Year growth (seasonality handling)

Seasonal decomposition (STL)

Forecasting layer (statsmodels / Prophet)

Budget allocation recommendations based on score

Automated orchestration (Makefile / scheduled runs)

👤 Author

Daniel Broadby
Tasmania, Australia