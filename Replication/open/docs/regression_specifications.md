# Regression specifications and prediction rules

Notation below is per NFT and respondent \(i\), with four states/ranges \(k,l \in \{1,2,3,4\}\).

- First-order belief: \(\mu_i^k\)
- Second-order belief: \(\alpha_i^l\)
- Instruments (recoded pre-quiz indicators): \(Z_{ip}\), \(p=1,\dots,6\)

Beliefs in raw data are percentages and are rescaled to \([0,1]\).

## Stage 1 (IV variants only)

For each \(k\), fit OLS:

\[
\mu_i^k = \gamma_{0k} + \sum_{p=1}^6 \gamma_{pk} Z_{ip} + u_i^k.
\]

Predicted regressors are \(\hat\mu_i^k\).

Instrument recoding (exactly matched to legacy code):

- `Pre_1 == 2`
- `Pre_2 == 3`
- `Pre_3 == 2`
- `Pre_4 == 3`
- `Pre_5 == 1`
- `Pre_6 == 3`

(each coded as 1/0).

For IV methods, rows with any \(\hat\mu_i^k < 0\) are dropped before Stage 2.

## Stage 2 PMBA regressions (six methods)

### 1) `ols_iv_c`
OLS, IV regressors, intercept, omitted-category form:

\[
\alpha_i^l = b_0^l + b_1^l\hat\mu_i^1 + b_2^l\hat\mu_i^2 + b_3^l\hat\mu_i^3 + \varepsilon_i^l.
\]

Recovered four-state coefficient row:
\[
[\bar\mu_1^l,\bar\mu_2^l,\bar\mu_3^l,\bar\mu_4^l]
= [b_1^l+b_0^l,\ b_2^l+b_0^l,\ b_3^l+b_0^l,\ b_0^l].
\]

### 2) `cls_iv_c`
Same equation as `ols_iv_c`, but constrained with logistic reparameterization
(component-wise \([0,1]\) bounds).

### 3) `ols_iv_nc`
No-intercept OLS with IV regressors:

\[
\alpha_i^l = \sum_{k=1}^4 b_k^l\hat\mu_i^k + \varepsilon_i^l.
\]

### 4) `cls_iv_nc`
Same as `ols_iv_nc`, but each coefficient constrained to \([0,1]\) via logistic map.

### 5) `ols_noiv_c`
Same as `ols_iv_c`, but uses raw \(\mu_i^k\) regressors (no Stage 1).

### 6) `cls_noiv_c`
Same as `cls_iv_c`, but uses raw \(\mu_i^k\) regressors (no Stage 1).

## PMBA prediction rule

For each NFT:

1. Compute respondent-average first-order beliefs:
   \(\hat\mu = (\overline{\mu^1},\overline{\mu^2},\overline{\mu^3},\overline{\mu^4})\).
2. Let `all_beta` be the 4x4 matrix from Stage 2; compare \(\hat\mu\) to rows of `all_beta^T`.
3. Use Euclidean distance and choose the nearest row index as predicted range.
4. Mark as “reasonable” if minimum distance `< 1.0`; else prediction set to `0`.

The final paper's rule (`eq:state_rule`) has no distance threshold: it takes the nearest row, with the
lowest index on ties. `final_paper.py` implements that rule directly. In this sample every method's
minimum distance is below 1, so step 4 never changes a prediction.

## Benchmark rules

- **Majority** (the paper's mean first-order belief rule): \(\arg\max_k\ \overline{\mu^k}\);
  the mean second-order belief rule uses \(\overline{\alpha^k}\) instead. Ties select the lowest range.
- **Plurality voting** (final paper only): each participant votes for her highest-probability range
  (lowest on ties); the range with most votes wins (lowest on ties).
- **SP group prediction**:
  - compute \(\mu_{12}=\overline{\mu^1}+\overline{\mu^2}\),
  - compute \(\alpha_{12}=\overline{\alpha^1}+\overline{\alpha^2}\),
  - predict `1&2` if \(\mu_{12}>\alpha_{12}\), else `3&4`.
