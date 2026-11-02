from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def run_correlations(data: pd.DataFrame, window: int = 60) -> None:
    Path("reports/figures").mkdir(parents=True, exist_ok=True)
    Path("reports/research").mkdir(parents=True, exist_ok=True)
    data.corr(method="pearson").to_csv("reports/research/pearson_correlation.csv")
    data.corr(method="spearman").to_csv("reports/research/spearman_correlation.csv")

    plt.figure(figsize=(10, 8))
    sns.heatmap(data.corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0)
    plt.title("Monthly changes: Pearson correlation")
    plt.tight_layout()
    plt.savefig("reports/figures/correlation_heatmap.png", dpi=160)
    plt.close()

    candidate_pairs = [("OIL", "FOOD"), ("OIL", "METALS"), ("OIL", "PRECIOUS"), ("OIL", "CPI")]
    pairs = [(a, b) for a, b in candidate_pairs if a in data.columns and b in data.columns]
    if pairs:
        rolling = pd.DataFrame({f"{a}_{b}": data[a].rolling(window).corr(data[b]) for a, b in pairs})
        rolling.to_csv("reports/research/rolling_correlations.csv")
        rolling.plot(figsize=(12, 5), title=f"{window}-month rolling correlation")
        plt.tight_layout()
        plt.savefig("reports/figures/rolling_correlations.png", dpi=160)
        plt.close()
