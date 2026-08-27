# Transform Functions

This document explains each function in `src/transform.py`, which cleans and validates raw order events before they're loaded into a query-friendly dataset.

---

## `parse_timestamp`

```python
def parse_timestamp(timestamp: str | None) -> datetime | None:
```

Converts a raw `event_timestamp` string into a real Python `datetime` object. If the value is missing, empty, or can't be parsed as a valid date, it returns `None`.

---

## `parse_items`

```python
def parse_items(items: str | None) -> list[dict]:
```

The `items` field in the raw data is stored as a Python-style literal string (single-quoted) rather than valid JSON, so it can't be parsed with `json.loads`. This function uses `ast.literal_eval` to safely convert it into a real Python list of dictionaries. If the field is missing or malformed, it returns an empty list rather than failing.

---

## `parse_shipping`

```python
def parse_shipping(shipping: str | None) -> dict:
```

Same idea as `parse_items`, but for the `shipping` field, which is a single dict literal string rather than a list. Returns a real Python dict on success, or an empty dict if the field is missing or invalid.

---

## `has_required_fields`

```python
REQUIRED_FIELDS = ["event_id", "event_type", "event_timestamp", "order_id"]

def has_required_fields(event: dict) -> bool:
```

Checks that an event has the four fields the pipeline can't function without: `event_id` (needed to identify), `event_type` (needed for order-status logic), `event_timestamp` (needed to order events within an order's lifecycle), and `order_id` (needed to group events by order). Returns `False` if any of these is missing, `None`, or an empty string.

---

## `remove_duplicate_events`

```python
def remove_duplicate_events(events: list[dict]) -> list[dict]:
```

Removes duplicate events based on `event_id`, keeping only the first occurrence of each one.

---

## `validate_quantities`

```python
def validate_quantities(items: list[dict]) -> bool:
```

Checks every item inside a parsed `items` list and returns `False` if any item has a missing, zero, or negative `qty`. A quantity of zero or less doesn't represent a real order line, so this flags the event as having invalid quantity data without discarding it outright.

---

## `clean_event`

```python
def clean_event(event: dict) -> dict | None:
```

Applies all the validation and parsing steps to a single raw event:

1. Drops the event (`return None`) if it fails `has_required_fields`.
2. Drops the event if `parse_timestamp` can't parse `event_timestamp`.
3. Otherwise, parses `items` and `shipping` into structured data, checks quantity validity with `validate_quantities`, and returns a cleaned event dictionary.

Fields like `order_total`, `unit_price`, and `shipping.region` are carried through, including `None` values.

---

## `clean_events`

```python
def clean_events(events: list[dict]) -> list[dict]:
```

The top-level entry point that ties everything together: it first removes duplicates with `remove_duplicate_events`, then runs `clean_event` over every remaining event, and finally filters out any event that came back as `None`.

---

## `group_by_order`

```python
def group_by_order(events: list[dict]) -> dict[str, list[dict]]:
```

Groups a list of cleaned events by `order_id`, producing a dictionary where each key is an order ID and each value is the list of that order's events.

---

## `is_order_active`

```python
ACTIVE_ORDER_EVENT = "order_paid"
TERMINAL_ORDER_EVENTS = {"order_delivered", "order_cancelled", "order_refunded"}

def is_order_active(order_events: list[dict]) -> bool:
```

Determines whether a single order is currently "active," per the case study spec: an order is active if it has a `order_paid` event, and does **not** have any of the terminal event types (`order_delivered`, `order_cancelled`, `order_refunded`).