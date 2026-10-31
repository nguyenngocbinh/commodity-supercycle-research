# Global Commodity Supercycle & Shock Transmission Research

Nghiên cứu định lượng siêu chu kỳ hàng hóa, tương quan liên thị trường và lan truyền cú sốc vĩ mô giai đoạn 2000–2030.

## Research questions
1. Giá hàng hóa có đồng bộ theo thời gian và có hình thành chu kỳ dài hạn không?
2. Cú sốc dầu có truyền sang thực phẩm, kim loại, CPI, USD và sản xuất công nghiệp không?
3. Phản ứng kéo dài bao lâu và mức độ bất định ra sao?
4. Bao nhiêu biến động dự báo của từng biến được giải thích bởi cú sốc dầu (FEVD)?
5. Kết quả có bền vững qua các giai đoạn và cách nhận diện cú sốc khác nhau không?

## Data sources
- **World Bank Pink Sheet**: giá hàng hóa quốc tế tháng (dầu Brent, ngô, lúa mì, đậu tương, đồng, nhôm, vàng, bạc).
- **FRED**: CPI (CPIAUCSL), broad trade-weighted USD (DTWEXBGS), Treasury 10Y (DGS10), Industrial Production (INDPRO).
- **EIA / USDA / IMF**: planned extensions for oil inventories, agricultural balances and cross-checks.

FRED API key is required. Create one at https://fred.stlouisfed.org/docs/api/api_key.html and set `FRED_API_KEY` in `.env` locally or GitHub Actions secrets.

## Quick start (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Add FRED_API_KEY to .env
python -m src.data.pipeline
python -m src.econometrics.run_analysis
```

## Baseline methodology
- Monthly frequency; start date configurable (default 2000-01-01).
- Convert positive price/index series to log changes; Treasury yield to first difference.
- Pearson/Spearman and rolling correlations.
- ADF and KPSS stationarity tests.
- VAR lag selection by AIC, stability diagnostics, Granger predictability, orthogonalized IRF and FEVD.
- Baseline Cholesky ordering: OIL, FOOD, METALS, PRECIOUS, CPI, USD, RATE, IP.

**Identification warning:** Cholesky IRFs depend on variable ordering. Reduced-form VAR and Granger tests do not establish structural causality. Any causal interpretation requires defensible restrictions, robustness checks and ideally external instruments or a separately identified SVAR.

## Repository structure
```
configs/                 model and source configuration
src/data/                World Bank and FRED extraction
src/features/            transformations and stationarity
src/econometrics/        correlation, VAR, IRF, FEVD
tests/                   unit tests
.github/workflows/       CI and scheduled research pipeline
data/raw/                downloaded source data (not committed)
data/processed/          aligned datasets (not committed)
reports/                 figures and model outputs (artifacts)
```

## Automation
- `ci.yml`: lint + unit tests on push and pull request.
- `monthly-research.yml`: monthly extraction and analysis; stores reports as a GitHub Actions artifact. Add repository secret `FRED_API_KEY`.

## Research quality controls
Report sample dates, observations, data source and extraction date; test alternative lag lengths and Cholesky orderings; inspect residual autocorrelation, heteroskedasticity and stability; compare sub-samples; avoid extrapolating a 2027–2030 scenario as a confirmed forecast.

## License / use
For research and educational purposes. Check each source's terms before redistributing downloaded data.
