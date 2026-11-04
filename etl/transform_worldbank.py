import pandas as pd
from pathlib import Path
from etl.json_types import read_json_records

def transform_worldbank_file(path: Path, code: str) -> pd.DataFrame:
    records = read_json_records(path)
    rows = []
    for r in records:
        country_info = r.get("country", {})
        iso3 = country_info.get("id") if isinstance(country_info, dict) else None
        val = r.get("value")
        year = r.get("date")
        rows.append({
            "country_iso3": iso3,
            "indicator_code": code,
            "year": year,
            "sex": "BTSX",
            "value": val
        })
    return pd.DataFrame(rows)

def transform_worldbank_countries(path: Path) -> pd.DataFrame:
    records = read_json_records(path)
    rows = []
    for r in records:
        region_info = r.get("region", {})
        region_name = region_info.get("value") if isinstance(region_info, dict) else ""
        if region_name == "Aggregates":
            continue
        rows.append({
            "country_code": r.get("id"),
            "name": r.get("name"),
            "region": region_name,
            "income_group": r.get("incomeLevel", {}).get("value") if isinstance(r.get("incomeLevel"), dict) else None
        })
    return pd.DataFrame(rows)