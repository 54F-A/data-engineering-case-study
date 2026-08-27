from datetime import datetime


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
