import io
import json
import time
from pathlib import Path
import requests

_DEFAULT_RAW_DIR = Path("data/raw/who")

class WhoApiError(Exception):
    pass

def _download_rows(code: str, year_from: int = 2000) -> tuple[list[dict], str]:
    base_url = f"https://ghoapi.azureedge.net/api/{code}"
    params = {"$filter": f"SpatialDimType eq 'COUNTRY' and TimeDim ge {year_from}"}
    rows = []
    next_url = base_url
    
    while next_url:
        # Reîncercare automată în caz de eroare temporară (503 / 500)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(next_url, params=params, timeout=120)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2)  # așteaptă 2 secunde înainte de a reîncerca

        payload = response.json()
        
        if not isinstance(payload, dict):
            raise WhoApiError(f"{next_url}: expected JSON dict, got {payload!r}")
            
        value = payload.get("value", [])
        if not isinstance(value, list):
            raise WhoApiError(f"{next_url}: 'value' is not a list: {value!r}")
            
        rows.extend(value)
        next_link = payload.get("@odata.nextLink")
        next_url = next_link if isinstance(next_link, str) else None
        params = None

    return rows, base_url

def _save_raw(output_dir: Path, filename: str, rows: list[dict]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return file_path

def download_who_indicator(code: str, year_from: int = 2000, *, output_dir: Path | None = None) -> tuple[Path, str]:
    rows, url = _download_rows(code, year_from)
    path = _save_raw(output_dir or _DEFAULT_RAW_DIR, f"{code}_from{year_from}.json", rows)
    return path, url