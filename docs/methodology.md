# Econometric methodology and interpretation

## 1. Transformations
Commodity prices and macro indices are transformed to one-month log changes. The 10-year
Treasury yield is transformed to a first difference in percentage points. These are candidate
stationary series, not a substitute for testing. ADF and KPSS are reported together.

## 2. Correlation
Pearson measures linear co-movement; Spearman measures rank association. Rolling correlations
are descriptive and can be unstable in short windows. Correlation is not causality.

## 3. VAR
The baseline VAR uses monthly changes and AIC lag selection up to 12 lags. Report sample size,
lag order, stability and residual diagnostics before interpretation. With eight endogenous
variables, parameter count grows quickly; compare a smaller parsimonious system and alternative
lag caps as robustness checks.

## 4. Granger predictability
A Granger test asks whether lagged oil changes improve prediction of another variable conditional
on the VAR information set. Rejection does not prove a structural causal effect.

## 5. IRF and identification
Orthogonalized IRFs use a Cholesky decomposition and therefore depend on the variable ordering.
The baseline ordering places OIL first, which imposes contemporaneous restrictions. Treat this as
a hypothesis to test, not an empirically established fact. Compare alternative orderings and
consider SVAR sign/zero restrictions or external instruments for structural oil-supply shocks.

## 6. FEVD
FEVD allocates forecast error variance to orthogonalized innovations. Its interpretation inherits
the identification assumptions of the IRF.

## 7. Robustness checklist
- Alternative lag caps (3, 6, 12) and information criteria (AIC, BIC, HQIC).
- Alternative Cholesky orderings.
- Subsamples and rolling estimation.
- Oil price returns versus identified oil-supply shock.
- Residual serial-correlation and heteroskedasticity tests.
- Confidence intervals for IRFs (bootstrap or Monte Carlo).
- Distinguish supply shocks, global demand shocks and precautionary demand shocks.

## 8. Scenario interpretation
A 20%, 30% or 50% oil price scenario is a scenario input, not a forecast. Do not multiply an
estimated one-standard-deviation IRF mechanically without checking linearity, scale and shock
identification. Report uncertainty and plausible alternative channels.
