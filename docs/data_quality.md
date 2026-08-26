# Data Quality Assessment

## 1. Overview

The raw order-event data was investigated before designing the ETL pipeline.

The purpose of this assessment was to identify data quality issues that could affect downstream reporting, analytics and order-status calculations.

The investigation covered:

- Dataset completeness
- Missing values
- Invalid values
- Duplicate events
- Inconsistent data structures
- Data types and formatting
- Values that could affect business logic

The detailed SQL investigation and findings are documented separately in [`data_quality_queries.md`](data_quality_queries.md).

---

## 2. Dataset Overview

The raw dataset contains **3,024 order events** across the supplied JSON files.

Each record represents an event in the lifecycle of an order, such as:

- Order created
- Order paid
- Order shipped
- Order delivered
- Order cancelled
- Order returned
- Order refunded

There are **800 unique valid order IDs** after excluding null or blank order IDs.

---

## 3. Data Quality Findings

### 3.1 Missing Order IDs

**Finding:** 33 records contain a missing or blank `order_id`.

**Impact:**

`order_id` is a key field used to associate events with an order. Records without an order ID cannot reliably be associated with an order lifecycle.

**Pipeline approach:**

Records with missing or blank order IDs should not be included in the final order-level dataset.

They should instead be identified and handled through the pipeline's data-quality/error handling process.

---

### 3.2 Missing Order Totals

**Finding:** 164 records contain a missing `order_total`.

**Impact:**

A missing order total prevents reliable financial analysis at event level.

**Pipeline approach:**

Retain the event where possible and represent the missing value as `NULL`.

---

### 3.3 Missing Shipping Regions

**Finding:** 354 records contain a missing shipping region.

**Impact:**

This can affect geographical reporting and analysis.

**Pipeline approach:**

Retain the record where possible and represent the missing region as `NULL`.

---

### 3.4 Missing Unit Prices

**Finding:** 126 item records contain a missing `unit_price`.

**Impact:**

Missing unit prices can affect calculations involving item-level revenue and order values.

**Pipeline approach:**

Retain the item where possible but preserve the missing price as `NULL`.

---

## 4. Invalid Data

### 4.1 Invalid Timestamps

**Finding:** 16 records contain timestamps that cannot be interpreted as valid timestamps.

**Impact:**

An invalid timestamp could result in incorrect identification of an order's latest status.

**Pipeline approach:**

Attempt to parse timestamps using safe conversion.

Invalid timestamps should be represented as `NULL` and excluded from chronological ordering.

---

### 4.2 Negative Quantities

**Finding:** 108 negative item quantities were identified.

**Impact:**

Negative quantities may represent invalid or unusual source data and could produce incorrect results in item-level analysis.

**Pipeline approach:**

Negative quantities should be identified during validation rather than silently converted to positive values.

The pipeline should preserve the original value and flag the record for data-quality handling.

Further business clarification would be required before deciding whether negative quantities represent a legitimate business scenario or invalid data.

---

### 4.3 Zero Quantities

**Finding:** 141 zero item quantities were identified.

**Impact:**

A quantity of zero may not represent a meaningful order item and could affect product and revenue analysis.

**Pipeline approach:**

Zero quantities should be identified during validation.

The original data should be preserved, while downstream reporting logic should determine whether zero-quantity items should be excluded.

---

## 5. Duplicate Events

**Finding:** 73 `event_id` values occur more than once.

The duplicate records were investigated to determine whether the repeated events represented different information or duplicated records.

The duplicated event IDs appear to contain identical data.

**Impact:**

If duplicate events are not removed, downstream calculations could over-count orders or events.

**Pipeline approach:**

Deduplicate events using `event_id` as the event-level identifier.

Where multiple records share the same `event_id`, retain a single record when the records are confirmed to represent the same event.

---

## 6. Inconsistent Data Structures

### 6.1 `items` and `shipping` Fields

The `items` and `shipping` fields are stored as string representations of Python dictionaries/lists rather than standard JSON structures.

--- 

## 7. ETL Implications

The data-quality investigation informs the design of the ETL pipeline.

The pipeline should therefore:

1. Read the raw JSON data without modifying the original source files.
2. Validate required fields such as `event_id` and `order_id`.
3. Safely parse timestamps and identify invalid values.
4. Deduplicate repeated events using `event_id`.
5. Parse the string-based `items` and `shipping` fields into structured data.
6. Validate item quantities and identify negative or zero values.
7. Preserve missing values as `NULL` where the record remains usable.
8. Retain currency information rather than assuming all monetary values are GBP.
9. Produce a clean, query-friendly output suitable for downstream analysis.
10. Keep data-quality handling explicit and reproducible.

---

## 8. Business Logic Considerations

The data-quality issues are particularly important when calculating order-level metrics.

For example, determining whether an order is currently active requires identifying the latest valid event for each order.

The pipeline must therefore:

- Exclude events with invalid timestamps from chronological ordering.
- Deduplicate repeated events.
- Group events by valid `order_id`.
- Determine the latest valid event for each order.
- Apply the business definition of an active order to that latest status.

This ensures that downstream reporting is based on the cleaned event history rather than the raw, potentially inconsistent data.