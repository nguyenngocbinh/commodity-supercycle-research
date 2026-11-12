from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

LANDING_PAGE = "https://www.worldbank.org/en/research/commodity-markets"


def discover_monthly_workbook() -> str:
    response = requests.get(LANDING_PAGE, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        label = anchor.get_text(" ", strip=True).lower()
        if href.lower().endswith(".xlsx") and (
            "monthly" in href.lower() or "monthly" in label
        ):
            links.append(requests.compat.urljoin(LANDING_PAGE, href))
    if not links:
        raise RuntimeError("Could not discover monthly XLSX from World Bank Commodity Markets page.")
    preferred = [u for u in links if "historical-data-monthly" in u.lower()]
    return preferred[0] if preferred else links[0]


def _header_row(raw: pd.DataFrame) -> int:
    """Find the monthly commodity header across World Bank workbook vintages.

    Recent Pink Sheet workbooks leave the first header cell blank, put
    commodity names on the header row, units on the next row, and monthly
    observations (YYYYMmm) below them. Older workbooks may label the first
    header cell as Period, Month, Date, or Time.
    """
    import re

    time_labels = ("date", "period", "month", "time")
    commodity_labels = (
        "copper",
        "crude oil",
        "brent",
        "aluminum",
        "aluminium",
        "gold",
        "silver",
        "wheat",
        "maize",
        "soybean",
        "natural gas",
        "coal",
        "coffee",
        "cocoa",
    )

    def is_month(value: object) -> bool:
        if pd.isna(value):
            return False
        return bool(re.fullmatch(r"\d{4}M\d{2}", str(value).strip(), flags=re.IGNORECASE))

    for i in range(min(40, len(raw))):
        row = raw.iloc[i].tolist()
        cells = [
            str(value).strip().lower() if pd.notna(value) else ""
            for value in row
        ]
        has_time_label = any(
            cell in time_labels or cell.startswith(("date ", "period ", "month "))
            for cell in cells[:2]
        )
        commodity_count = sum(
            any(label in cell for label in commodity_labels)
            for cell in cells[1:]
        )

        if has_time_label and commodity_count:
            return i

        # Current Pink Sheet layout: blank first header cell, commodity names,
        # optional units row, then monthly periods such as 1960M01.
        if commodity_count >= 2:
            for offset in range(1, 4):
                next_row = i + offset
                if next_row >= len(raw):
                    break
                if is_month(raw.iloc[next_row, 0]):
                    return i

    raise ValueError(
        "Could not locate the monthly header row in World Bank Pink Sheet workbook. "
        f"Available first rows: {raw.head(8).fillna('').astype(str).values.tolist()}"
    )


def download_monthly_prices(output_dir: str = "data/raw") -> pd.DataFrame:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    url = discover_monthly_workbook()
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    (out / "world_bank_pink_sheet_monthly.xlsx").write_bytes(response.content)

    excel = pd.ExcelFile(BytesIO(response.content))
    sheet = next((s for s in excel.sheet_names if "monthly" in s.lower()), excel.sheet_names[0])
    raw = pd.read_excel(BytesIO(response.content), sheet_name=sheet, header=None)
    header = _header_row(raw)
    data = pd.read_excel(BytesIO(response.content), sheet_name=sheet, header=header)
    date_col = data.columns[0]
    date_text = data[date_col].astype(str).str.strip()
    parsed = pd.to_datetime(
        date_text.str.replace(r"(\d{4})M(\d{2})", r"\1-\2", regex=True),
        errors="coerce",
    )
    data = data.loc[parsed.notna()].copy()
    data.index = parsed.loc[parsed.notna()].dt.to_period("M").dt.to_timestamp()
    data.index.name = "date"
    data = data.drop(columns=[date_col])
    for column in data:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_index()
    data.to_csv(out / "world_bank_monthly_prices.csv")
    return data
