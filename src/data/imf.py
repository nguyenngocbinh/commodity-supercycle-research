from __future__ import annotations

from io import StringIO
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import requests

BASE_URL = "https://api.imf.org/external/sdmx/2.1/data/IMF.RES,PCPS"
DEFAULT_SERIES = {
    "imf_brent": "POILBRE",
    "imf_oil_average": "POILAPSP",
    "imf_nonfuel_commodities_index": "PALLFNF",
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_xml(content: bytes, column: str) -> pd.DataFrame:
    root = ET.fromstring(content)
    rows = []
    for obs in root.iter():
        if _local_name(obs.tag) != "Obs":
            continue
        period = value = None
        for child in obs.iter():
            name = _local_name(child.tag)
            if name == "ObsDimension":
                period = child.attrib.get("value")
            elif name == "ObsValue":
                value = child.attrib.get("value")
        if period and value not in (None, ""):
            rows.append((period, value))
    if not rows:
        raise ValueError("IMF SDMX response contained no observations.")
    frame = pd.DataFrame(rows, columns=["date", column])
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["date"]).set_index("date")[[column]]


def _parse_response(response: requests.Response, column: str) -> pd.DataFrame:
    body = response.content
    content_type = response.headers.get("Content-Type", "").lower()
    if "xml" in content_type or body.lstrip().startswith(b"<?xml"):
        return _parse_xml(body, column)

    frame = pd.read_csv(StringIO(response.text.lstrip("\ufeff")))
    columns = {str(c).strip().upper(): c for c in frame.columns}
    date_col = next((columns[k] for k in ("TIME_PERIOD", "TIME", "PERIOD") if k in columns), None)
    value_col = next((columns[k] for k in ("OBS_VALUE", "OBSERVED_VALUE", "VALUE") if k in columns), None)
    if date_col is None or value_col is None:
        raise ValueError(f"Unexpected IMF CSV columns: {list(frame.columns)}")
    frame = frame[[date_col, value_col]].rename(columns={date_col: "date", value_col: column})
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["date"]).set_index("date")[[column]]


def download_pcps(
    start_date: str = "2000-01-01",
    end_date: str | None = None,
    output_dir: str = "data/raw",
    indicators: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Download public global monthly IMF PCPS observations in nominal USD."""
    selected = indicators or DEFAULT_SERIES
    params = {"startPeriod": pd.Timestamp(start_date).strftime("%Y-%m")}
    if end_date:
        params["endPeriod"] = pd.Timestamp(end_date).strftime("%Y-%m")
    frames = []
    for column, indicator in selected.items():
        key = f"G001.{indicator}.USD.M"
        response = requests.get(
            f"{BASE_URL}/{key}",
            params=params,
            headers={"Accept": "application/vnd.sdmx.data+csv;version=2.0.0"},
            timeout=90,
        )
        response.raise_for_status()
        frames.append(_parse_response(response, column))
    if not frames:
        raise RuntimeError("No IMF PCPS indicators configured.")
    result = pd.concat(frames, axis=1).sort_index()
    result.index = result.index.to_period("M").to_timestamp()
    result.index.name = "date"
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "imf_pcps_monthly.csv")
    return result
