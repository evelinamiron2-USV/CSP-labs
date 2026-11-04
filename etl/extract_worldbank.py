import json
from pathlib import Path
import requests

_DEFAULT_RAW_DIR = Path("data/raw/worldbank")

class WorldBankApiError(Exception):
    pass

def download_worldbank_indicator(code: str, output_dir: Path | None = None) -> tuple[Path, str]:
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=1000"
    records = []
    page = 1
    
    while True:
        page_url = f"{url}&page={page}"
        response = requests.get(page_url, timeout=120)
        response.raise_for_status()
        body = response.json()
        
        if not (isinstance(body, list) and len(body) == 2):
            raise WorldBankApiError(f"{page_url}: unexpected response {body!r}")
            
        meta, data = body
        if not isinstance(meta, dict) or "pages" not in meta:
            raise WorldBankApiError(f"{page_url}: missing page metadata in {meta!r}")
            
        records.extend(data or [])
        if page >= int(meta["pages"]):
            break
        page += 1

    out_dir = output_dir or _DEFAULT_RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{code}.json"
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        
    return path, url

def download_worldbank_countries(output_dir: Path | None = None) -> tuple[Path, str]:
    url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    body = response.json()
    
    meta, data = body
    out_dir = output_dir or _DEFAULT_RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "countries.json"
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data or [], f, ensure_ascii=False, indent=2)
        
    return path, url