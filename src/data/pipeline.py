from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

from src.data.fred import download_fred
from src.data.world_bank import download_monthly_prices


def match_column(columns, aliases):
    normalized = {str(col).strip().lower(): col for col in columns}
    for alias in aliases:
        for label, original in normalized.items():
            if alias.lower() == label or alias.lower() in label:
                return original
    raise KeyError(f"Unable to match aliases {aliases}; workbook columns: {list(columns)}")


def build_monthly_dataset(start_date: str | None = None) -> pd.DataFrame:
    load_dotenv()
    start_date = start_date or os.getenv("START_DATE", "2000-01-01")
    config = yaml.safe_load(Path("configs/variables.yaml").read_text(encoding="utf-8"))
    wb = download_monthly_prices()
    fred = download_fred(start_date=start_date)

    selected = {}
    for key, aliases in config["world_bank"].items():
        selected[key] = wb[match_column(wb.columns, aliases)].rename(key)
    commodity = pd.concat(selected.values(), axis=1)
    commodity = commodity.loc[pd.Timestamp(start_date):]
    merged = commodity.join(fred, how="outer").sort_index()
    merged = merged[~merged.index.duplicated(keep="last")]
    merged.index.name = "date"

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    merged.to_csv("data/processed/monthly_levels.csv")
    return merged


if __name__ == "__main__":
    data = build_monthly_dataset()
    print(f"Saved {data.shape} observations: {data.index.min()} - {data.index.max()}")
