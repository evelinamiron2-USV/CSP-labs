import io
from pathlib import Path
import pandas as pd
import requests

_DEFAULT_RAW_DIR = Path("data/raw/owid")

def download_owid_chart(slug: str, output_dir: Path | None = None) -> tuple[Path, str]:
    url = f"https://ourworldindata.org/grapher/{slug}.csv"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
    response.raise_for_status()
    
    out_dir = output_dir or _DEFAULT_RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.csv"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    return path, url