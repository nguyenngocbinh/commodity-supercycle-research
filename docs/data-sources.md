# Data sources and extraction contract

## Selected providers

- World Bank Commodity Markets Pink Sheet: monthly nominal commodity prices. Required primary source for the commodity price panel.
- IMF Primary Commodity Price System (PCPS): public SDMX 2.1 dataflow, global aggregate G001, nominal USD transformation, monthly frequency. Selected indicators: POILBRE (Brent), POILAPSP (average oil price), PALLFNF (non-fuel commodity index).
- US Energy Information Administration (EIA): optional US monthly crude oil field production and crude oil stocks. These are US-only measures, not global supply or global inventories.

## API and credentials

- IMF PCPS: public SDMX API; no API key is configured here.
- World Bank Pink Sheet: public monthly workbook download; no API key.
- EIA: free API key required. Store it as EIA_API_KEY in local .env or GitHub Actions Secrets. Never commit credentials.

## Outputs

- data/raw/world_bank_pink_sheet_monthly.xlsx
- data/raw/world_bank_monthly_prices.csv
- data/raw/imf_pcps_monthly.csv
- data/raw/eia_monthly.csv (when EIA_API_KEY is configured)
- data/processed/monthly_levels.csv
- data/processed/source_manifest.json

The manifest records extraction timestamp, source status, row counts, columns, sample coverage and missing-value shares. Provider failures are not converted to zero. IMF is optional enrichment by default; set REQUIRE_ALL_SOURCES=true to fail the run if an enabled provider fails.

## Frequency and methodology

The analytical panel is monthly. Daily or weekly series must be aggregated using an explicitly documented method before inclusion. This initial EIA adapter uses monthly series only. Do not upsample annual or quarterly series to monthly by repeating values.

## Attribution and licensing

Retain source metadata and cite the original publisher. Check each provider's terms before redistributing raw or processed data. Public API access does not imply unrestricted redistribution rights.
