from pathlib import Path
import json
from typing import Any

def save_data(data: Any, filename: Path):
    """Save data to a JSON file."""
    try:
        with filename.open('w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}.")
    except IOError as e:
        print(f"Could not save to {filename}: {e}")

def load_data(filename: Path) -> Any:
    """Load data from a JSON file with validation."""
    if not filename.exists():
        return None
    try:
        with filename.open('r') as f:
            data = json.load(f)
            return data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Could not load or parse {filename}: {e}")
        return None