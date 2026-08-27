from src.extract import extract_events
from src.transform import clean_events, group_by_order, is_order_active
from src.load import load_json


def build_order_summary(cleaned_events: list[dict]) -> list[dict]:
    """
    Build one summary row per order, showing its current active status,
    ready to directly answer business questions about active orders.
    """

    orders = group_by_order(cleaned_events)
    summary = []

    for order_id, order_events in orders.items():
        first_event = order_events[0]
        summary.append({
            "order_id": order_id,
            "customer_id": first_event.get("customer_id"),
            "is_active": is_order_active(order_events),
            "event_count": len(order_events),
        })

    return summary


def main() -> None:
    raw_events = extract_events("data/raw")
    print(f"Extracted {len(raw_events)} events")

    cleaned_events = clean_events(raw_events)
    print(f"Cleaned dataset: {len(cleaned_events)} events "
          f"({len(raw_events) - len(cleaned_events)} dropped)")

    load_json(cleaned_events, "data/processed/events.json")

    order_summary = build_order_summary(cleaned_events)
    load_json(order_summary, "data/processed/order_summary.json")
    print(f"Order summary: {len(order_summary)} orders "
          f"({sum(o['is_active'] for o in order_summary)} active)")

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()