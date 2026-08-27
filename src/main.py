from extract import extract_events
from transform import parse_timestamp
from load import load_json


def main() -> None:
    raw_events = extract_events("data/raw")

    print(f"Extracted {len(raw_events)} events")

    for event in raw_events:
        event["parsed_timestamp"] = parse_timestamp(
            event.get("event_timestamp")
        )

    load_json(raw_events, "data/processed/events.json")

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()