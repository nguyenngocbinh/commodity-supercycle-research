# Econometric methodology and interpretation

## 1. Transformations
Commodity prices and positive indices are transformed to one-month log changes. The 10-year
Treasury yield, if added by a future macroeconomic provider, should be transformed to a first
difference in percentage points. ADF and KPSS are reported together.

## 2. Baseline data scope
The selected IMF + World Bank + EIA source stack supports a commodity-only monthly VAR:
OIL, FOOD, METALS and PRECIOUS. EIA series in the initial implementation are US crude-oil
production and US crude-oil stocks; they are auxiliary US indicators and must not be described
as global supply or inventories. CPI, USD, interest rates and industrial production are not
provided by this three-source configuration and are therefore not fabricated or imputed.

## 3. Correlation
Pearson measures linear co-movement; Spearman measures rank association. Rolling correlations
are descriptive and can be unstable in short windows. Correlation is not causality.

## 4. VAR
The commodity-only baseline VAR uses monthly changes and AIC lag selection, with a maximum lag
cap of 12 subject to sample size. Report sample size, lag order, stability and residual diagnostics
before interpretation. A larger model with macro variables should be estimated only after
adding documented monthly CPI, USD, rate and industrial-production series.

## 5. Granger predictability
A Granger test asks whether lagged oil changes improve prediction of another variable conditional
on the VAR information set. Rejection does not prove a structural causal effect.

## 6. IRF and identification
Orthogonalized IRFs use a Cholesky decomposition and therefore depend on variable ordering.
The baseline ordering places OIL first, which imposes contemporaneous restrictions. Treat this as
a hypothesis to test, not an empirically established fact. Compare alternative orderings and
consider SVAR sign/zero restrictions or external instruments for structural oil-supply shocks.

## 7. FEVD
FEVD allocates forecast error variance to orthogonalized innovations. Its interpretation inherits
the identification assumptions of the IRF.

## 8. Robustness checklist
- Alternative lag caps (3, 6, 12) and information criteria (AIC, BIC, HQIC).
- Alternative Cholesky orderings.
- Subsamples and rolling estimation.
- Oil price returns versus identified oil-supply shock.
- Residual serial-correlation and heteroskedasticity tests.
- Confidence intervals for IRFs (bootstrap or Monte Carlo).
- Distinguish supply shocks, global demand shocks and precautionary demand shocks.

## 9. Scenario interpretation
A 20%, 30% or 50% oil price scenario is a scenario input, not a forecast. Do not multiply an
estimated one-standard-deviation IRF mechanically without checking linearity, scale and shock
identification. Report uncertainty and plausible alternative channels.
