from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

from src.data.eia import download_eia_monthly
from src.data.imf import download_pcps
from src.data.world_bank import download_monthly_prices

LOGGER = logging.getLogger(__name__)


def match_column(columns, aliases):
    normalized = {str(col).strip().lower(): col for col in columns}
    for alias in aliases:
        for label, original in normalized.items():
            if alias.lower() == label or alias.lower() in label:
                return original
    raise KeyError(f"Unable to match aliases {aliases}; workbook columns: {list(columns)}")


def _select_world_bank_columns(wb: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    selected = {}
    for key, names in aliases.items():
        try:
            selected[key] = wb[match_column(wb.columns, names)].rename(key)
        except KeyError:
            LOGGER.warning("World Bank series '%s' not found; skipping.", key)
    if not selected:
        raise RuntimeError("No configured World Bank columns matched the downloaded workbook.")
    result = pd.concat(selected.values(), axis=1)
    result.index = pd.to_datetime(result.index).to_period("M").to_timestamp()
    return result


def _optional_provider(name: str, loader, required: bool):
    try:
        frame = loader()
        return frame, {"status": "success", "rows": len(frame), "columns": list(frame.columns)}
    except Exception as exc:
        if required:
            raise
        LOGGER.warning("%s provider unavailable; continuing: %s", name, exc)
        return None, {"status": "failed_or_skipped", "error": str(exc)}


def build_monthly_dataset(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    load_dotenv()
    start_date = start_date or os.getenv("START_DATE", "2000-01-01")
    end_date = end_date or os.getenv("END_DATE")
    config = yaml.safe_load(Path("configs/variables.yaml").read_text(encoding="utf-8"))
    required = os.getenv("REQUIRE_ALL_SOURCES", "false").lower() == "true"

    wb = download_monthly_prices()
    wb_selected = _select_world_bank_columns(wb, config["world_bank"]).loc[pd.Timestamp(start_date):]
    frames = [wb_selected]
    manifest = {
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_date": start_date,
        "end_date": end_date,
        "sources": {
            "world_bank": {
                "status": "success",
                "rows": len(wb_selected),
                "columns": list(wb_selected.columns),
            }
        },
    }

    imf_cfg = config.get("imf", {})
    if imf_cfg.get("enabled", True):
        imf, status = _optional_provider(
            "IMF",
            lambda: download_pcps(start_date, end_date, indicators=imf_cfg.get("indicators")),
            required,
        )
        manifest["sources"]["imf"] = status
        if imf is not None:
            frames.append(imf)

    eia_cfg = config.get("eia", {})
    if eia_cfg.get("enabled", True) and os.getenv("EIA_API_KEY"):
        eia, status = _optional_provider(
            "EIA",
            lambda: download_eia_monthly(start_date, series=eia_cfg.get("series")),
            required,
        )
        manifest["sources"]["eia"] = status
        if eia is not None:
            frames.append(eia)
    else:
        manifest["sources"]["eia"] = {"status": "not_configured", "note": "Set EIA_API_KEY to enable EIA."}

    merged = pd.concat(frames, axis=1, join="outer").sort_index()
    merged = merged.loc[pd.Timestamp(start_date):]
    if end_date:
        merged = merged.loc[:pd.Timestamp(end_date)]
    merged = merged[~merged.index.duplicated(keep="last")]
    merged.index = merged.index.to_period("M").to_timestamp()
    merged.index.name = "date"

    out = Path("data/processed")
    out.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out / "monthly_levels.csv")
    manifest["dataset"] = {
        "rows": len(merged),
        "columns": list(merged.columns),
        "first_observation": merged.index.min().strftime("%Y-%m-%d") if not merged.empty else None,
        "last_observation": merged.index.max().strftime("%Y-%m-%d") if not merged.empty else None,
        "missing_share_by_column": merged.isna().mean().round(6).to_dict(),
    }
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    data = build_monthly_dataset()
    print(f"Saved {data.shape} observations: {data.index.min()} - {data.index.max()}")
