# E-Commerce Order Data Pipeline

An ETL pipeline that reads raw e-commerce order-event JSON data, cleans and transforms it, and produces a clean, queryable dataset for downstream reporting and analysis.

## Solution Design

The pipeline follows a simple **Extract → Transform → Load** structure:

- **Extract** (`src/extract.py`) — reads all raw JSON event files from `data/raw/`, one JSON object per line.
- **Transform** (`src/transform.py`) — validates required fields, parses timestamps and nested `items`/`shipping` fields, removes duplicate events, validates item quantities, and derives order status (active/inactive).
- **Load** (`src/load.py`) — writes the cleaned data to `data/processed/` as query-friendly JSON, queryable directly with DuckDB.

`src/main.py` wires these stages together into a single entry point, producing two output files:
- `data/processed/events.json` — cleaned, deduplicated event-level data
- `data/processed/order_summary.json` — one row per order, with derived active status

See [`pipeline_flow.jpg`](docs/pipeline_flow.jpg) for the full pipeline data flow diagram.

## How to Run It

1. Install dependencies:
```bash
   pip install -r requirements.txt
```

2. Run the pipeline from the project root:
```bash
   python -m src.main
```

3. Query the output with [DuckDB](https://duckdb.org/):
```bash
   duckdb
```
```sql
   SELECT * FROM read_json_auto('data/processed/events.json') LIMIT 5;
```

See [`business_questions_queries.md`](docs/business_questions_queries.md) for the exact queries used to answer the case study's business questions.
