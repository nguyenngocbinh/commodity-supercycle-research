import numpy as np
import pandas as pd

from src.features.transformations import log_change, build_model_data


def test_log_change():
    values = pd.Series([100.0, 110.0, 121.0])
    result = log_change(values)
    assert np.isnan(result.iloc[0])
    assert np.isclose(result.iloc[1], np.log(1.1))


def test_model_data_columns_and_length():
    idx = pd.date_range("2000-01-01", periods=40, freq="MS")
    raw = pd.DataFrame({
        "brent": np.linspace(30, 70, 40),
        "corn": np.linspace(100, 140, 40),
        "wheat": np.linspace(90, 130, 40),
        "soybean": np.linspace(200, 250, 40),
        "copper": np.linspace(1, 2, 40),
        "aluminum": np.linspace(.5, 1, 40),
        "gold": np.linspace(300, 500, 40),
        "silver": np.linspace(4, 8, 40),
        "cpi": np.linspace(170, 220, 40),
        "usd": np.linspace(100, 110, 40),
        "rate": np.linspace(2, 4, 40),
        "ip": np.linspace(80, 100, 40),
    }, index=idx)
    model = build_model_data(raw)
    assert list(model.columns) == ["OIL", "FOOD", "METALS", "PRECIOUS", "CPI", "USD", "RATE", "IP"]
    assert len(model) == 39


def test_commodity_only_model_without_macro_provider():
    idx = pd.date_range("2000-01-01", periods=48, freq="MS")
    raw = pd.DataFrame({
        "brent": np.linspace(30, 70, 48),
        "corn": np.linspace(100, 140, 48),
        "wheat": np.linspace(90, 130, 48),
        "soybean": np.linspace(200, 250, 48),
        "copper": np.linspace(1, 2, 48),
        "aluminum": np.linspace(.5, 1, 48),
        "gold": np.linspace(300, 500, 48),
        "silver": np.linspace(4, 8, 48),
    }, index=idx)
    model = build_model_data(raw)
    assert list(model.columns) == ["OIL", "FOOD", "METALS", "PRECIOUS"]
    assert len(model) == 47
