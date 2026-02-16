import os
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "raw", "chocolate_sales.csv")

df = pd.read_csv(csv_path)

# Rename columns to match our raw table
df = df.rename(columns={
    "Sales Person": "sales_person",
    "Country": "country",
    "Product": "product",
    "Date": "sale_date_raw",
    "Amount": "amount_raw",
    "Boxes Shipped": "boxes_shipped_raw",
})

# Load into raw schema/table
df.to_sql("chocolate_sales", engine, schema="raw", if_exists="replace", index=False)

print("Loaded rows:", len(df))
