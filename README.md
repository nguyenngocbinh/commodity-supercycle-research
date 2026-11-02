# Global Commodity Supercycle & Shock Transmission Research

Nghiên cứu định lượng siêu chu kỳ hàng hóa, tương quan liên thị trường và lan truyền cú sốc vĩ mô giai đoạn 2000–2030.

## Research questions
1. Giá hàng hóa có đồng bộ theo thời gian và có hình thành chu kỳ dài hạn không?
2. Cú sốc dầu có truyền sang thực phẩm, kim loại, CPI, USD và sản xuất công nghiệp không?
3. Phản ứng kéo dài bao lâu và mức độ bất định ra sao?
4. Bao nhiêu biến động dự báo của từng biến được giải thích bởi cú sốc dầu (FEVD)?
5. Kết quả có bền vững qua các giai đoạn và cách nhận diện cú sốc khác nhau không?

## Data sources

| Provider | Coverage | Access |
|---|---|---|
| World Bank Pink Sheet | Monthly international commodity prices: Brent, maize, wheat, soybeans, copper, aluminium, gold, silver | Public XLSX, no API key |
| IMF PCPS | Monthly global commodity benchmarks and indices: Brent, average oil, non-fuel commodity index | Public SDMX API |
| US EIA | US monthly crude oil field production and crude oil stocks | Free API key |

Important scope note: EIA series currently configured are US measures, not global production, consumption or inventories. Do not label them as global supply/demand. Expand to global series only after selecting and documenting suitable international EIA series.

The IMF provider queries the global aggregate G001, nominal USD transformation and monthly frequency. See the [IMF API documentation](https://data.imf.org/en/Resource-Pages/IMF-API) and [PCPS dataset](https://data.imf.org/en/datasets/IMF.RES:PCPS).

EIA is optional. Register for a free key at https://www.eia.gov/opendata/register.php and store it as EIA_API_KEY in local .env or GitHub Actions Secrets. IMF and World Bank do not require API keys. Never commit .env or credentials.

## Quick start (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Optional: add EIA_API_KEY to .env
python -m src.data.pipeline
python -m src.econometrics.run_analysis
```

World Bank monthly prices are the required primary input. IMF is optional enrichment by default; EIA runs when EIA_API_KEY is configured. Set REQUIRE_ALL_SOURCES=true to fail the run if an enabled provider fails. Missing observations are never replaced with zero.

## Data outputs
- data/raw/world_bank_pink_sheet_monthly.xlsx
- data/raw/world_bank_monthly_prices.csv
- data/raw/imf_pcps_monthly.csv
- data/raw/eia_monthly.csv (when EIA is enabled)
- data/processed/monthly_levels.csv
- data/processed/source_manifest.json

The source manifest records extraction timestamp, provider status, sample coverage, columns and missing-value shares. See docs/data-sources.md for the extraction contract.

## Baseline methodology
- Monthly frequency; start date configurable (default 2000-01-01).
- Convert positive price/index series to log changes; use first differences for rates when a suitable macro source is added.
- Pearson/Spearman and rolling correlations.
- ADF and KPSS stationarity tests.
- VAR lag selection by AIC, stability diagnostics, Granger predictability, orthogonalized IRF and FEVD.
- Baseline Cholesky ordering: OIL, FOOD, METALS, PRECIOUS, CPI, USD, RATE, IP.

Identification warning: Cholesky IRFs depend on variable ordering. Reduced-form VAR and Granger tests do not establish structural causality. Any causal interpretation requires defensible restrictions, robustness checks and ideally external instruments or a separately identified SVAR.

## Repository structure
```
configs/                 source and model configuration
src/data/world_bank.py   World Bank Pink Sheet extraction
src/data/imf.py          IMF PCPS SDMX extraction
src/data/eia.py          EIA petroleum series extraction
src/data/pipeline.py     monthly alignment and source manifest
src/features/            transformations and stationarity
src/econometrics/        correlation, VAR, IRF, FEVD
tests/                   unit tests
.github/workflows/       CI and scheduled research pipeline
data/raw/                downloaded source data (not committed)
data/processed/          aligned datasets (not committed)
reports/                 figures and model outputs
```

## Automation
- ci.yml: lint + unit tests on push and pull request.
- monthly-research.yml: scheduled on the 5th at 09:30 Vietnam time. Add repository secret EIA_API_KEY to enable EIA. IMF and World Bank run without credentials.
- Review source terms before redistributing downloaded data or derived datasets.

## Research quality controls
Record sample dates, observations, provider, extraction date and source definitions; test alternative lag lengths and Cholesky orderings; inspect residual autocorrelation, heteroskedasticity and stability; compare sub-samples; do not extrapolate a 2027–2030 scenario as a confirmed forecast.

## License / use
For research and educational purposes. Cite the original provider and check each source's terms before redistributing downloaded data.
