# Data Quality Investigation

## 1. Dataset Overview

### Initial Data Preview

Reads both raw JSON files as a single combined table and previews the first 5 rows to confirm the schema loads correctly.

```sql
SELECT *
FROM read_json_auto('data/raw/*.json')
LIMIT 5;
```

### Total Events

Counts the total number of events across both raw JSON files.

```sql
SELECT COUNT(*) AS total_events
FROM read_json_auto('data/raw/*.json');
```

Finding:
3,024 raw events...

### Unique Orders

Counts the number of distinct, non-empty order IDs across all events, filtering out any null or blank values.

```sql
SELECT COUNT(DISTINCT order_id) AS unique_orders
FROM read_json_auto('data/raw/*.json')
WHERE order_id IS NOT NULL
AND TRIM(order_id) <> '';
```

Finding:
800 unique valid orders...

## 2. Missing Data

### Missing Order IDs

Counts events with a null or blank `order_id`.

```sql
SELECT COUNT(*) AS missing_order_ids
FROM read_json_auto('data/raw/*.json')
WHERE order_id IS NULL
OR TRIM(order_id) = '';
```

Finding:
33 missing order ids...

### Missing Order Totals

Counts events where `order_total` is null.

```sql
SELECT COUNT(*) AS missing_order_totals
FROM read_json_auto('data/raw/*.json')
WHERE order_total IS NULL;
```

Finding:
164 missing order totals...

### Missing Shipping Regions

Checks for missing `region` values inside the `shipping` field.

```sql
SELECT COUNT(*) AS missing_shipping_regions
FROM read_json_auto('data/raw/*.json')
WHERE shipping LIKE '%''region'': None%'
   OR shipping LIKE '%''region'': ''''%';
```

Finding:
354 missing shipping regions...

### Missing Unit Prices

Splits `items` into individual item objects and checks for missing `unit_price` values inside the `items` field.

```sql
WITH item_objs AS (
    SELECT UNNEST(regexp_extract_all(items, '\{[^}]*\}')) AS item_obj
    FROM read_json_auto('data/raw/*.json')
)
SELECT COUNT(*) AS missing_unit_prices
FROM item_objs
WHERE item_obj LIKE '%''unit_price'': None%'
   OR item_obj LIKE '%''unit_price'': ''''%';
```

Finding:
126 missing unit prices...

## 3. Invalid Data

### Invalid Timestamps

Finds rows where the `timestamp` field cannot be cast to a valid `TIMESTAMP`.

```sql
SELECT
    event_id,
    order_id,
    event_type,
    event_timestamp
FROM read_json_auto('data/raw/*.json')
WHERE TRY_CAST(event_timestamp AS TIMESTAMP) IS NULL;
```

Finding:
16 invalid rows...

### Negative Quantities

Checks for negative `qty` values inside the `items` field (Since `items` is stored as a Python string, quantities are extracted with a regex rather than JSON parsing).

```sql
SELECT COUNT(*) AS negative_quantities
FROM (
    SELECT UNNEST(regexp_extract_all(items, '''qty''\s*:\s*(-?\d+)', 1)) AS qty_str
    FROM read_json_auto('data/raw/*.json')
)
WHERE CAST(qty_str AS INTEGER) < 0;
```

Finding:
108 negative quantities...

Breaks down negative `qty` values inside `items` by `event_type`.

```sql
SELECT
    event_type,
    COUNT(*) AS negative_quantity_events
FROM (
    SELECT
        event_type,
        UNNEST(regexp_extract_all(items, '''qty''\s*:\s*(-?\d+)', 1)) AS qty_str
    FROM read_json_auto('data/raw/*.json')
)
WHERE CAST(qty_str AS INTEGER) < 0
GROUP BY event_type
ORDER BY negative_quantity_events DESC;
```

### Zero Quantities

Checks for `qty` values of exactly 0 inside `items`.

```sql
SELECT COUNT(*) AS zero_quantities
FROM (
    SELECT UNNEST(regexp_extract_all(items, '''qty''\s*:\s*(-?\d+)', 1)) AS qty_str
    FROM read_json_auto('data/raw/*.json')
)
WHERE CAST(qty_str AS INTEGER) = 0;
```

Finding:
141 zero quantities...

Breaks the zero-quantity check down by `event_type`.

```sql
SELECT
    event_type,
    COUNT(*) AS zero_quantity_events
FROM (
    SELECT
        event_type,
        UNNEST(regexp_extract_all(items, '''qty''\s*:\s*(-?\d+)', 1)) AS qty_str
    FROM read_json_auto('data/raw/*.json')
)
WHERE CAST(qty_str AS INTEGER) = 0
GROUP BY event_type
ORDER BY zero_quantity_events DESC;
```


## 4. Duplicate Events

### Duplicated Event Count

Counts how many distinct `event_id` values appear more than once.

```sql
SELECT
    COUNT(*) AS duplicated_events
FROM (
    SELECT event_id
    FROM read_json_auto('data/raw/*.json')
    GROUP BY event_id
    HAVING COUNT(*) > 1
);
```

Finding:
73 event IDs occur more than once.

Groups events by `event_id` to check whether any event appears more than once across the two files.

```sql
SELECT
    event_id,
    COUNT(*) AS occurrence_count
FROM read_json_auto('data/raw/*.json')
GROUP BY event_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;
```
