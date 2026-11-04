import pandas as pd
from pathlib import Path

def transform_owid_file(path: Path, code: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    value_cols = [c for c in df.columns if c not in ("Entity", "Code", "Year")]
    val_col = value_cols[0] if value_cols else None

    return pd.DataFrame({
        "country_iso3": df.get("Code"),
        "indicator_code": code,
        "year": df.get("Year"),
        "sex": "BTSX",
        "value": df.get(val_col) if val_col else None
    })