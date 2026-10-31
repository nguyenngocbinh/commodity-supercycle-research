from __future__ import annotations

import numpy as np
import pandas as pd


def log_change(series: pd.Series) -> pd.Series:
    """One-period log change; non-positive observations are treated as missing."""
    values = pd.to_numeric(series, errors="coerce")
    return np.log(values.where(values > 0)).diff()


def build_model_data(levels: pd.DataFrame) -> pd.DataFrame:
    """Build stationary candidate series for baseline monthly VAR."""
    out = pd.DataFrame(index=levels.index)
    out["OIL"] = log_change(levels["brent"])
    out["FOOD"] = pd.concat(
        [log_change(levels[c]) for c in ["corn", "wheat", "soybean"]], axis=1
    ).mean(axis=1)
    out["METALS"] = pd.concat(
        [log_change(levels[c]) for c in ["copper", "aluminum"]], axis=1
    ).mean(axis=1)
    out["PRECIOUS"] = pd.concat(
        [log_change(levels[c]) for c in ["gold", "silver"]], axis=1
    ).mean(axis=1)
    out["CPI"] = log_change(levels["cpi"])
    out["USD"] = log_change(levels["usd"])
    out["RATE"] = pd.to_numeric(levels["rate"], errors="coerce").diff()
    out["IP"] = log_change(levels["ip"])
    return out.replace([np.inf, -np.inf], np.nan).dropna()
