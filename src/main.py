from src.extract import extract_events
from src.transform import clean_events
from src.load import load_json


def main() -> None:
    raw_events = extract_events("data/raw")
    print(f"Extracted {len(raw_events)} events")

    cleaned_events = clean_events(raw_events)
    print(f"Cleaned dataset: {len(cleaned_events)} events "
          f"({len(raw_events) - len(cleaned_events)} dropped)")

    load_json(cleaned_events, "data/processed/events.json")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()