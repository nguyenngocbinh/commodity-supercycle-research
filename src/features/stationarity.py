import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss


def stationarity_report(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in data.columns:
        series = data[name].dropna()
        adf = adfuller(series, autolag="AIC")
        kp = kpss(series, regression="c", nlags="auto")
        rows.append({
            "variable": name, "adf_stat": adf[0], "adf_pvalue": adf[1],
            "kpss_stat": kp[0], "kpss_pvalue": kp[1], "nobs": len(series),
        })
    return pd.DataFrame(rows).set_index("variable")
