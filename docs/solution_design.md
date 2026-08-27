# Solution Design

## 1. Objective

Build a reproducible ETL pipeline that reads the raw order-event JSON data, cleans and transforms the data, and produces a query-friendly dataset for downstream reporting and analysis.

The pipeline must be able to answer the two business questions provided in the case study:

1. How many customers currently have an active order?
2. How many orders were shipped in 2024, split by product category?

---

## 2. Pipeline Approach

The pipeline will follow a simple Extract, Transform and Load structure.

### Extract

Read all raw JSON order-event files from `data/raw/`.

The raw source files will remain unchanged.

### Transform

The transformation stage will:

- Validate required fields.
- Parse and standardise timestamps.
- Remove confirmed duplicate events.
- Handle invalid timestamps.
- Parse the `items` and `shipping` fields into structured data.
- Validate item quantities.
- Preserve missing values where appropriate.
- Retain currency information.
- Apply the required order-status logic.

### Load

Write the cleaned and transformed data into a query-friendly format that can be queried using SQL.

---
