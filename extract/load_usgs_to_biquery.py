"""
Load the USGS Combined Wildland Fire Dataset (CSV) into BigQuery raw layer.

Source: USGS Combined Wildland Fire Datasets for the United States and
Certain Territories, 1800s-Present (DOI: 10.5066/P9ZXGFY3)

This script:
1. Reads the raw CSV locally with everything as string (matches the
   all-STRING raw staging schema decision).
2. Cleans stray/unbalanced quote characters in known problem columns
   (see docs/ for notes on why this is needed).
3. Loads the cleaned data into BigQuery, replacing any existing table.

Run from the project root:
    python extract/load_usgs_to_bigquery.py
"""

import pandas as pd
from google.cloud import bigquery

# --- Config ---
CSV_PATH = "data/raw/USGS_Wildland_Fire_Combined_Dataset.csv"
PROJECT_ID = "wildfire-trends"          # TODO: replace with your actual GCP project ID
DATASET_ID = "wildfire_trends_raw"
TABLE_ID = "usgs_fires"

# Columns known to contain stray/unbalanced quote characters that break
# strict CSV parsers (confirmed via notebook investigation). Balanced
# doubled-quote pairs (e.g. in Listed_Fire_Names) are left alone since
# those are valid, intentional characters in the source data.
COLUMNS_TO_CLEAN = ["Listed_Notes"]


def load_and_clean_csv(path: str) -> pd.DataFrame:
    """Read the CSV as all-string and strip stray quote characters
    from known problem columns."""
    df = pd.read_csv(path, dtype=str)
    print(f"Read {len(df)} rows, {len(df.columns)} columns from {path}")

    for col in COLUMNS_TO_CLEAN:
        if col in df.columns:
            before = df[col].astype(str).str.count('"').sum()
            df[col] = df[col].astype(str).str.replace('"', "", regex=False)
            after = df[col].astype(str).str.count('"').sum()
            print(f"Cleaned '{col}': removed {before - after} stray quote characters")

    return df


def load_to_bigquery(df: pd.DataFrame) -> None:
    """Load a DataFrame into BigQuery, replacing the existing table.
    All columns are loaded as STRING to match the raw layer convention:
    raw data should never fail to load due to type mismatches. Type
    casting happens later in the staging transform step.
    """
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        schema=[bigquery.SchemaField(col, "STRING") for col in df.columns],
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # wait for the job to complete

    table = client.get_table(table_ref)
    print(f"Loaded {job.output_rows} rows into {table_ref}")
    print(f"Table now has {table.num_rows} total rows")


if __name__ == "__main__":
    df = load_and_clean_csv(CSV_PATH)
    load_to_bigquery(df)