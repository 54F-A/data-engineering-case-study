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
