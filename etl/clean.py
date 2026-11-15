import logging
import pandas as pd
from app.models import Sex

logger = logging.getLogger(__name__)

_KEY_COLUMNS = ["country_iso3", "indicator_code", "year", "sex"]

def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]

def clean_observations(df: pd.DataFrame, valid_iso3: set = None) -> pd.DataFrame:
    if df.empty:
        return df

    cleaned = df.copy()

    # 1. Filtrare țări: dacă se dă valid_iso3, filtrăm doar codurile invalide/goale
    cleaned = _drop(cleaned, cleaned["country_iso3"].isna() | (cleaned["country_iso3"] == ""), "missing country iso3")
    if valid_iso3:
        cleaned = _drop(cleaned, ~cleaned["country_iso3"].isin(valid_iso3), "invalid country iso3")

    # 2. Conversie an și valoare
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = _drop(cleaned, cleaned["year"].isna() | cleaned["value"].isna(), "missing or non-numeric year/value")

    # 3. Ani întregi (2000 - 2024)
    cleaned["year"] = cleaned["year"].astype(int)
    cleaned = _drop(cleaned, (cleaned["year"] < 2000) | (cleaned["year"] > 2024), "year out of window (2000-2024)")

    # 4. Sex implicit
    if "sex" not in cleaned.columns:
        cleaned["sex"] = Sex.BOTH.value
    else:
        cleaned["sex"] = cleaned["sex"].fillna(Sex.BOTH.value)

    # 5. Deduplicare
    cleaned = _drop(cleaned, cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"), "duplicate key")

    return cleaned