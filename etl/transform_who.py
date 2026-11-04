import pandas as pd
from pathlib import Path
from etl.json_types import read_json_records

_SEX_DIMENSION = "SEX"

def transform_who_file(path: Path, code: str) -> pd.DataFrame:
    records = read_json_records(path)
    if not records:
        return pd.DataFrame(columns=["country_iso3", "indicator_code", "year", "sex", "value"])

    raw = pd.DataFrame(records)

    if "Dim1" in raw.columns and "Dim1Type" in raw.columns:
        dim1_type = raw["Dim1Type"]
        raw = raw[dim1_type.isna() | (dim1_type == _SEX_DIMENSION)]
        sex = raw["Dim1"].where(raw["Dim1Type"] == _SEX_DIMENSION)
    else:
        sex = None

    return pd.DataFrame({
        "country_iso3": raw.get("SpatialDim"),
        "indicator_code": code,
        "year": raw.get("TimeDim"),
        "sex": sex,
        "value": raw.get("NumericValue")
    })