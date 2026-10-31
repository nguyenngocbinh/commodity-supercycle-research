from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

API_URL = "https://api.stlouisfed.org/fred/series/observations"
SERIES = {
    "cpi": "CPIAUCSL",
    "usd": "DTWEXBGS",
    "rate": "DGS10",
    "ip": "INDPRO",
}


def download_fred(start_date: str = "2000-01-01", output_dir: str = "data/raw") -> pd.DataFrame:
    load_dotenv()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is missing. Add it to .env or GitHub Actions secrets.")

    frames = []
    for name, series_id in SERIES.items():
        params = {
            "series_id": series_id, "api_key": api_key, "file_type": "json",
            "observation_start": start_date, "sort_order": "asc",
        }
        response = requests.get(API_URL, params=params, timeout=45)
        response.raise_for_status()
        observations = response.json().get("observations", [])
        frame = pd.DataFrame(observations)
        if frame.empty:
            continue
        frame["date"] = pd.to_datetime(frame["date"])
        frame[name] = pd.to_numeric(frame["value"].replace(".", pd.NA), errors="coerce")
        frames.append(frame.set_index("date")[[name]])

    if not frames:
        raise RuntimeError("FRED returned no observations.")

    result = pd.concat(frames, axis=1).sort_index().resample("MS").mean()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    result.to_csv(Path(output_dir) / "fred_monthly.csv")
    return result
