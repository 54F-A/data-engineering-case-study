from pathlib import Path
import json


def load_json(data: list[dict], output_path: str) -> None:
    """
    Write transformed data to a JSON file.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, default=str)
