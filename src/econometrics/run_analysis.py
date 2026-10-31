from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from statsmodels.tsa.api import VAR

from src.econometrics.correlation import run_correlations
from src.features.stationarity import stationarity_report
from src.features.transformations import build_model_data

ORDER = ["OIL", "FOOD", "METALS", "PRECIOUS", "CPI", "USD", "RATE", "IP"]


def main():
    Path("reports/research").mkdir(parents=True, exist_ok=True)
    Path("reports/figures").mkdir(parents=True, exist_ok=True)
    levels = pd.read_csv("data/processed/monthly_levels.csv", index_col=0, parse_dates=True)
    model_data = build_model_data(levels)
    model_data.to_csv("data/processed/model_data.csv")
    stationarity_report(model_data).to_csv("reports/research/stationarity.csv")
    run_correlations(model_data)

    model_data = model_data[ORDER].dropna()
    selection = VAR(model_data).select_order(maxlags=12)
    lag = max(1, int(selection.selected_orders.get("aic") or 1))
    fitted = VAR(model_data).fit(lag, trend="c")
    Path("reports/research/var_summary.txt").write_text(str(fitted.summary()), encoding="utf-8")
    Path("reports/research/lag_selection.txt").write_text(str(selection.summary()), encoding="utf-8")

    diagnostics = {
        "selected_lag_aic": lag, "is_stable": bool(fitted.is_stable()),
        "nobs": int(fitted.nobs), "start": str(model_data.index.min().date()),
        "end": str(model_data.index.max().date()),
    }
    Path("reports/research/var_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )

    rows = []
    for caused in ORDER[1:]:
        test = fitted.test_causality(caused=caused, causing=["OIL"], kind="f")
        rows.append({
            "cause": "OIL", "effect": caused, "statistic": float(test.test_statistic),
            "pvalue": float(test.pvalue), "significant_5pct": bool(test.pvalue < 0.05),
        })
    pd.DataFrame(rows).to_csv("reports/research/granger_oil_to_others.csv", index=False)

    irf = fitted.irf(24)
    fig = irf.plot(orth=True, impulse="OIL")
    fig.suptitle("Orthogonalized responses to one-SD oil shock (Cholesky)")
    fig.tight_layout()
    fig.savefig("reports/figures/oil_shock_irf.png", dpi=160)
    import matplotlib.pyplot as plt
    plt.close(fig)

    fevd = fitted.fevd(24)
    fevd_rows = []
    for i, variable in enumerate(ORDER):
        for h in range(24):
            for j, shock in enumerate(ORDER):
                fevd_rows.append({
                    "variable": variable, "horizon": h + 1, "shock": shock,
                    "share": float(fevd.decomp[i, h, j]),
                })
    pd.DataFrame(fevd_rows).to_csv("reports/research/fevd.csv", index=False)
    print(f"Analysis complete. VAR({lag}); stable={fitted.is_stable()}; nobs={fitted.nobs}")


if __name__ == "__main__":
    main()
