# Wildfire Trends — United States

A data pipeline and analysis project examining whether wildfires in the United States have grown more frequent and intense over the past several decades, with a focus on the western states. Built as a hands-on project to practice ELT pipeline design on Google Cloud Platform (BigQuery).

**Scope note:** Phase 1 covers the United States only. Canada (British Columbia, Alberta) is planned as a future extension to expand the analysis to western North America.

## Motivation

Wildfires have appeared to grow more intense over the last 10 years. This project pulls together public wildfire data to explore that trend quantitatively — acres burned per year, number of large fires, and geographic patterns — rather than relying on anecdote.

## Data Sources

| Source | Coverage | Format | Access |
|---|---|---|---|
| [USGS Combined Wildland Fire Datasets](https://doi.org/10.5066/P9ZXGFY3) (Welty & Jeffries, 2021) | 1835–2020 | CSV (attribute table export) | One-time bulk download from ScienceBase |
| [NIFC WFIGS Interagency Fire Perimeters](https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters/about) | 2021–present | GeoJSON | ArcGIS REST Feature Service (queryable API) |

The USGS dataset provides deep historical coverage but was last published in 2021 and does not include recent fire seasons. WFIGS fills that gap with certified perimeters from 2021 onward. Together, they provide a continuous record from the 1800s through the present.

See `docs/Wildland_Fire_Polygon_Metaadata.xml` for full field definitions and data lineage.

**Note:** The USGS release is distributed as a File Geodatabase, GeoJSON, or CSV attribute table export. This project uses the **CSV Attribute Table Exports** file, which contains fire attributes (name, ID, date, size, cause) without full polygon geometry — sufficient for year-over-year trend analysis without the overhead of handling spatial geometry files.

## Architecture

This project follows an **ELT** (Extract, Load, Transform) pattern:

```
┌─────────────┐     ┌─────────────┐     ┌───────────────┐     ┌───────────────┐
│   Extract   │ ──> │  Load (raw) │ ──> │  Transform    │ ──> │  Visualize    │
│  USGS CSV / │     │  GCS bucket │     │  BigQuery SQL │     │  Looker Studio│
│  NIFC API   │     │  → BigQuery │     │  (staging →   │     │  or Python    │
│             │     │  staging    │     │   clean)      │     │  (pandas)     │
└─────────────┘     └─────────────┘     └───────────────┘     └───────────────┘
```

1. **Extract** — Download the USGS historical CSV (one-time bulk pull) and query the NIFC WFIGS API for recent perimeters (2021–present).
2. **Load** — Land raw files, untouched, in a GCS bucket, then load into BigQuery staging tables.
3. **Transform** — Use BigQuery SQL to clean, standardize schemas between sources, filter to western states, and aggregate into analysis-ready tables (e.g., acres burned per year).
4. **Visualize** — Connect BigQuery to Looker Studio (or query via Python/pandas) to chart trends.

## Tech Stack

- **Cloud platform:** Google Cloud Platform
- **Data warehouse:** BigQuery
- **Storage (data lake):** Google Cloud Storage
- **Language:** Python
- **Visualization:** Looker Studio (primary), pandas/matplotlib (optional secondary)

## Project Structure

```
wildfire-trends/
├── README.md
├── .gitignore
├── requirements.txt
├── extract/          # Scripts to pull data from USGS and NIFC API
├── transform/        # SQL transformation queries
├── sql/              # BigQuery table/view DDL
└── notebooks/        # Exploratory analysis (optional)
```

## Data Access

Raw data files are not committed to this repository due to size. To reproduce:

1. Download the USGS CSV Attribute Table Exports from the [ScienceBase item page](https://www.sciencebase.gov/catalog/item/61707c2ad34ea36449a6b066).
2. NIFC WFIGS data is pulled programmatically via the ArcGIS REST API — no manual download needed (see `extract/`).

## Status

🚧 In progress — currently building the extract/load pipeline for the USGS historical dataset.

## Roadmap

- [ ] Load USGS CSV into BigQuery staging
- [ ] Build extract script for NIFC WFIGS API
- [ ] Write SQL transforms (western states filter, annual aggregation)
- [ ] Build Looker Studio dashboard
- [ ] Extend to Canadian data (CWFIS / National Fire Database)