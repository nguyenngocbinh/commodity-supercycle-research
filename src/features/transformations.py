from __future__ import annotations

import numpy as np
import pandas as pd


def log_change(series: pd.Series) -> pd.Series:
    """One-period log change; non-positive observations are treated as missing."""
    values = pd.to_numeric(series, errors="coerce")
    return np.log(values.where(values > 0)).diff()


def _group_log_change(levels: pd.DataFrame, columns: list[str]) -> pd.Series:
    available = [column for column in columns if column in levels.columns]
    if not available:
        return pd.Series(index=levels.index, dtype=float)
    changes = pd.concat([log_change(levels[column]) for column in available], axis=1)
    return changes.mean(axis=1, skipna=True)


def build_model_data(levels: pd.DataFrame) -> pd.DataFrame:
    """Build stationary candidates from available monthly sources.

    Commodity-only VAR remains usable without a macroeconomic API subscription.
    CPI, USD, RATE and IP are added only when those level series are supplied.
    """
    out = pd.DataFrame(index=levels.index)

    oil_column = "brent" if "brent" in levels.columns else "imf_brent"
    if oil_column not in levels.columns:
        raise KeyError("A Brent price series is required (brent or imf_brent).")
    out["OIL"] = log_change(levels[oil_column])

    groups = {
        "FOOD": ["corn", "wheat", "soybean"],
        "METALS": ["copper", "aluminum"],
        "PRECIOUS": ["gold", "silver"],
    }
    for name, columns in groups.items():
        series = _group_log_change(levels, columns)
        if series.notna().any():
            out[name] = series

    if "cpi" in levels.columns:
        out["CPI"] = log_change(levels["cpi"])
    if "usd" in levels.columns:
        out["USD"] = log_change(levels["usd"])
    if "rate" in levels.columns:
        out["RATE"] = pd.to_numeric(levels["rate"], errors="coerce").diff()
    if "ip" in levels.columns:
        out["IP"] = log_change(levels["ip"])

    return out.replace([np.inf, -np.inf], np.nan).dropna()
