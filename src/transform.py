from datetime import datetime
import ast


def parse_timestamp(timestamp: str | None) -> datetime | None:
    """
    Safely parse an event timestamp.

    Returns None when the timestamp is missing or invalid.
    """

    if not timestamp:
        return None

    try:
        return datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return None

def parse_items(items: str | None) -> list[dict]:
    """
    Safely parse the `items` field, which is stored as a Python-style
    literal string rather than valid JSON.

    Returns an empty list when the field is missing or invalid.
    """

    if not items:
        return []

    try:
        parsed = ast.literal_eval(items)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []

def parse_shipping(shipping: str | None) -> dict:
    """
    Safely parse the `shipping` field, which is stored as a Python-style
    literal string rather than valid JSON.

    Returns an empty dict when the field is missing or invalid.
    """

    if not shipping:
        return {}

    try:
        parsed = ast.literal_eval(shipping)
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, SyntaxError):
        return {}

REQUIRED_FIELDS = ["event_id", "event_type", "event_timestamp", "order_id"]


def has_required_fields(event: dict) -> bool:
    """
    Check that an event contains all required fields with non-empty values.

    Returns False if any required field is missing, None, or an empty string.
    """

    for field in REQUIRED_FIELDS:
        value = event.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False

    return True

def remove_duplicate_events(events: list[dict]) -> list[dict]:
    """
    Remove duplicate events based on event_id, keeping the first occurrence.
    """

    seen_ids = set()
    unique_events = []

    for event in events:
        event_id = event.get("event_id")

        if event_id in seen_ids:
            continue

        seen_ids.add(event_id)
        unique_events.append(event)

    return unique_events

def validate_quantities(items: list[dict]) -> bool:
    """
    Check whether all items have a valid (positive) quantity.

    Returns False if any item has a missing, zero, or negative qty.
    """

    for item in items:
        qty = item.get("qty")
        if qty is None or qty <= 0:
            return False

    return True


def clean_event(event: dict) -> dict | None:
    """
    Clean and validate a single raw event.

    Returns None if the event should be dropped.
    """

    if not has_required_fields(event):
        return None

    parsed_timestamp = parse_timestamp(event.get("event_timestamp"))
    if parsed_timestamp is None:
        return None

    items = parse_items(event.get("items"))
    shipping = parse_shipping(event.get("shipping"))

    return {
        "event_id": event.get("event_id"),
        "event_type": event.get("event_type"),
        "event_timestamp": parsed_timestamp,
        "order_id": event.get("order_id"),
        "customer_id": event.get("customer_id"),
        "order_total": event.get("order_total"),
        "currency": event.get("currency"),
        "channel": event.get("channel"),
        "items": items,
        "has_valid_quantities": validate_quantities(items),
        "shipping": shipping,
        "payment_method": event.get("payment_method"),
    }


def clean_events(events: list[dict]) -> list[dict]:
    """
    Deduplicate and clean a list of raw events, dropping any event
    that fails required-field or timestamp validation.
    """

    deduped = remove_duplicate_events(events)
    cleaned = [clean_event(e) for e in deduped]

    return [e for e in cleaned if e is not None]

ACTIVE_ORDER_EVENT = "order_paid"
TERMINAL_ORDER_EVENTS = {"order_delivered", "order_cancelled", "order_refunded"}


def group_by_order(events: list[dict]) -> dict[str, list[dict]]:
    """
    Group cleaned events by order_id.
    """

    orders: dict[str, list[dict]] = {}

    for event in events:
        order_id = event["order_id"]
        orders.setdefault(order_id, []).append(event)

    return orders


def is_order_active(order_events: list[dict]) -> bool:
    """
    Determine whether an order is currently active: it has been paid,
    but has not yet been delivered, cancelled, or refunded.
    """

    event_types = {e["event_type"] for e in order_events}

    if ACTIVE_ORDER_EVENT not in event_types:
        return False

    if event_types & TERMINAL_ORDER_EVENTS:
        return False

    return True
