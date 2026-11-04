import json
from pathlib import Path

def read_json_records(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}, got {type(data)}")
    return data

def require_keys(record: dict, keys: list[str]) -> None:
    for key in keys:
        if key not in record:
            raise KeyError(f"Missing required key '{key}' in record {record}")