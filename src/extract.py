from pathlib import Path
import json


def extract_events(data_path: str) -> list[dict]:
    """
    Extract order events from JSON files in the supplied directory.
    Each line in the source files represents one JSON event.
    """

    events = []

    for file_path in sorted(Path(data_path).glob("*.json")):
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                events.append(json.loads(line))

    return events

if __name__ == "__main__":
    events = extract_events("data/raw")
    print(f"Loaded {len(events)} events")