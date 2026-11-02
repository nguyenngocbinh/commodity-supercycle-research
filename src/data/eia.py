from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

BASE_URL = "https://api.eia.gov/v2/seriesid"
# US series only. Weekly stocks are converted to month-end observations.
DEFAULT_SERIES = {
    "eia_us_crude_oil_field_production": "PET.MCRFPUS2.M",
    "eia_us_crude_oil_stocks": "PET.WCESTUS1.W",
}


def download_eia_monthly(
    start_date: str = "2000-01-01",
    output_dir: str = "data/raw",
    series: dict[str, str] | None = None,
) -> pd.DataFrame:
    load_dotenv()
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise RuntimeError("EIA_API_KEY is missing. Register for a free key at https://www.eia.gov/opendata/register.php")
    frames = []
    for column, series_id in (series or DEFAULT_SERIES).items():
        try:
            response = requests.get(
                f"{BASE_URL}/{series_id}",
                params={"api_key": api_key, "length": 5000},
                timeout=90,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            # Never propagate request URLs: the EIA key is passed as a query parameter.
            status = getattr(getattr(exc, "response", None), "status_code", None)
            detail = f"HTTP {status}" if status else type(exc).__name__
            raise RuntimeError(f"EIA request failed for {series_id}: {detail}") from None
        except ValueError:
            raise RuntimeError(f"EIA returned invalid JSON for {series_id}.") from None

        rows = payload.get("response", {}).get("data", [])
        if not rows:
            raise RuntimeError(f"EIA returned no observations for {series_id}.")
        frame = pd.DataFrame(rows)
        if not {"period", "value"}.issubset(frame.columns):
            raise ValueError(f"Unexpected EIA schema for {series_id}: {list(frame.columns)}")
        frame["date"] = pd.to_datetime(frame["period"], errors="coerce")
        frame[column] = pd.to_numeric(frame["value"], errors="coerce")
        series_frame = frame.dropna(subset=["date"]).set_index("date")[[column]].sort_index()
        if series_id.endswith(".W"):
            # Month-end stock: retain the last available weekly observation in each month.
            series_frame = series_frame.resample("ME").last()
        series_frame.index = series_frame.index.to_period("M").to_timestamp()
        frames.append(series_frame)
    result = pd.concat(frames, axis=1).sort_index()
    result = result.loc[pd.Timestamp(start_date):]
    result.index.name = "date"
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "eia_monthly.csv")
    return result
