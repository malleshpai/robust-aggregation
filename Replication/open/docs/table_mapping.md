# Mapping from generated files to the paper

Paper source: `../../paper/main.tex` (relative to `Replication/open/`).

All final-paper outputs are written by `make final` to `outputs/final_paper/` (abbreviated `FP/` below)
from the raw data. `make check-final` compares each number with the value printed in the paper and
writes `FP/final_paper_check.md`. The printed values are transcribed, with their table labels, in
`src/replication_open/final_paper_expectations.py`; the check keys (first column of the report) start
with the label they come from. The computations are in `src/replication_open/final_paper.py`.

Rules used throughout, as stated in the paper: the PMBA prediction is the smallest state minimising the
Euclidean distance between the fitted state-contingent mean vector and the mean first-order belief
(rule `eq:state_rule`, no distance threshold); mean-belief rules and plurality voting select the lowest
range on individual and aggregate ties; SP assigns ties to high (3&4).

## Section 4 (Experimental evidence), text numbers

| Paper statement | Output | Check keys |
|---|---|---|
| 199 participants, 10 NFTs each | `FP/summary.json` (`sample`) | `sec4:sample/*` |
| 93 to 104 participants per NFT; six participant-NFT pairs dropped; first-stage F from 0.23 to 3.96 | `FP/summary.json` (`first_stage`), `FP/table_firststage.csv` | `sec4:implementation/*` |
| Gains of 0.15 to 0.30 categories, 11-19% of benchmark MAE | `FP/table_prediction_errors.csv` | `sec4:results/*` |
| Uncertainty: differences -0.25, -0.15; 95% paired t intervals [-0.55, 0.05], [-0.50, 0.20]; t p = 0.0481; signed-rank p = 0.0938 | `FP/summary.json` (`uncertainty_and_where`) | `sec4:uncertainty/*` |
| Where the difference comes from: 5 better, 14 unchanged, 1 worse; items 1, 3, 6, 13 raised, 18 lowered, 10 worse | `FP/summary.json` (`uncertainty_and_where`) | `sec4:where/*` |
| Constant Range 2: MAE 0.85, 7 exact, never off by more than 2 | `FP/summary.json` (`constant_range2`) | `sec4:constant_range2/*` |
| Binary SP: PMBA 12 of 20, SP 10, McNemar p = 0.7539 | `FP/summary.json` (`binary_sp`), `FP/table_score_comparison.csv` | `sec4:sp/*` |
| All three benchmarks predict Range 1 for every Range 4 item | `FP/table_item_predictions.csv` | `sec4:discussion/*` |
| Validity: 320 components, 94 negative, 18 above one, 208 (65%) in [0,1]; selected vector out of bounds for 17 of 20 NFTs | `FP/summary.json` (`validity`), `FP/figure_data/state_contingent_means.csv` | `sec4:validity/n_*`, `share_within_pct`, `selected_out_of_bounds` |
| Alternative matching: PMBA beats all benchmarks on MAE in every specification; valid-coordinate rules 7 or 8 exact vs at most 5; coordinate 1 or 4 alone 4 and 3 exact vs 5 | `FP/summary.json` (`alternative_matching_text`), `FP/table_alternative_matching_summary.csv` | `sec4:validity/*exact*`, `pmba_specs_beat_all_benchmarks_on_mae` |

## Tables

| Paper table | Output | Check keys |
|---|---|---|
| `tab:prediction_errors` | `FP/table_prediction_errors.csv` | `tab:prediction_errors/*` |
| `tab:true_range` | `FP/table_true_range.csv` | `tab:true_range/*` |
| `tab:item_predictions` (rows, by-range summaries, Wilcoxon and paired t p-values for range subsets) | `FP/table_item_predictions.csv`, `FP/table_true_range.csv`, `FP/table_item_predictions_tests.csv` | `tab:item_predictions/*` |
| `tab:score_comparison` (rows, average scores, totals, McNemar/Wilcoxon/t p-values) | `FP/table_score_comparison.csv`, `FP/table_score_comparison_tests.csv` | `tab:score_comparison/*` |
| `alternative-matching` (landscape table) | `FP/table_alternative_matching.csv` (also has the omitted Own>=4 column), `FP/table_alternative_matching_summary.csv` | `alternative-matching/*` |
| `tab:rob1` | `FP/table_robustness.csv`, `FP/table_robustness_summary.csv` | `tab:rob1/*` |
| `tab:firststage` | `FP/table_firststage.csv` | `tab:firststage/*` |
| `tab:nft_list` | Range column = `../data/raw/true_state.csv`; prices are not in the raw data and are only checked for internal consistency | `tab:nft_list/*` |
| `tab:sp_replication` | `FP/table_sp_replication.csv` | `tab:sp_replication/*` |

`FP/item_level.csv` collects every per-NFT quantity (predictions under all rules, first-stage F,
retained sample, SP inputs and p-values) in one file.

## Figures

| Paper figure | Data | Redrawn figure | Check keys |
|---|---|---|---|
| `fig:state_mean_distribution` (`State_contingent_Vec_dist.png`) | `FP/figure_data/state_contingent_means.csv` (320 components), `FP/figure_data/component_histogram.csv` (panel a, bins of width 0.2), `FP/figure_data/vector_sums.csv` (panel b) | `FP/figures/state_contingent_vec_dist.png` | `fig:state_mean_distribution/*` (legend counts and shares, every bar of panel a, 80 vectors summing to one) |
| `validity` (`valid_grid.png`) | `FP/figure_data/validity_grid.csv` (N = below 0, V = in [0,1], A = above 1; 16 cells per NFT, candidate state by coordinate) | `FP/figures/valid_grid.png` | `fig:validity/*` (every cell, read from the paper's image) |

Panel (b) of `fig:state_mean_distribution` prints a maximum adding-up error of 2.00e-15. That number is
floating-point rounding noise and depends on the platform and linear-algebra library, so the check only
requires it to be below 1e-12; the report notes the value this run obtains.

## Notes on the rules behind specific numbers

- `tab:sp_replication` p-values: one-sided one-sample t test of the individual reports
  alpha_i(1&2) against the null mean mu_hat(1&2), in the direction of the observed difference. (Testing
  mu_i(1&2) against the mean of alpha(1&2), as `paper_tables.py` does for the original submission,
  gives different p-values that do not match the final paper.)
- First-stage F: classical F for the six quiz indicators with (6, n-7) degrees of freedom on all
  participants who rated the NFT; "retained" counts participants with no negative fitted first-order
  probability.
- Alternative matching, Own >= k: for each candidate state keep its coordinates in [0, 1]; the
  candidate is eligible with at least k of them and is scored by the root mean square of its gaps from
  mean first-order beliefs over those coordinates; lowest state wins ties.

## Check against the original submission

`make tables` and `make check-paper` reproduce the tables of the original submission, in that
submission's layout, and compare them with values hard-coded in `src/replication_open/paper_expectations.py`.

- Rows: `outputs/tables/table_prediction_accuracy.csv`, `table_score_comparison.csv`,
  `table_robustness_predictions.csv`, `table_sp_replication.csv`
- Summaries: `outputs/tables/*_summary.json`
- LaTeX row snippets: `outputs/tables/latex/`
- Report: `outputs/tables/paper_crosscheck_report.md` (and `.json`)

These files are kept for continuity; the final paper is checked by `make check-final`.
