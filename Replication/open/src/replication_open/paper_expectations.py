"""Table values from the ORIGINAL submission, used by `make check-paper`.

The final paper is checked against final_paper_expectations.py (`make check-final`).
"""
from __future__ import annotations

PAPER_NFT_ORDER = [
    2, 11, 17, 18,
    7, 8, 9, 10, 13, 15, 19,
    1, 4, 6, 12, 14,
    3, 5, 16, 20,
]

# Table: Prediction Accuracy: PMBA vs Majority Voting (tab:prediction_errors)
PREDICTION_ERRORS_EXPECTED = {
    2: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    11: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    17: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    18: {"pmba": 2, "majority_mu": 3, "majority_alpha": 3},
    7: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    8: {"pmba": 3, "majority_mu": 1, "majority_alpha": 2},
    9: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    10: {"pmba": 4, "majority_mu": 1, "majority_alpha": 1},
    13: {"pmba": 2, "majority_mu": 1, "majority_alpha": 1},
    15: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    19: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    1: {"pmba": 3, "majority_mu": 1, "majority_alpha": 1},
    4: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    6: {"pmba": 4, "majority_mu": 1, "majority_alpha": 1},
    12: {"pmba": 4, "majority_mu": 2, "majority_alpha": 3},
    14: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    3: {"pmba": 2, "majority_mu": 1, "majority_alpha": 1},
    5: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    16: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
    20: {"pmba": 1, "majority_mu": 1, "majority_alpha": 1},
}

PREDICTION_ERRORS_SUMMARY_EXPECTED = {
    "mae_pmba": 1.25,
    "mae_majority_mu": 1.50,
    "mae_majority_alpha": 1.40,
    "wilcoxon_p_vs_majority_mu": 0.0938,
    "wilcoxon_p_vs_majority_alpha": 0.2812,
    "ttest_p_vs_majority_mu": 0.0481,
    "ttest_p_vs_majority_alpha": 0.1896,
}

# Table: PMBA vs SP (tab:score_comparison)
SCORE_COMPARISON_SUMMARY_EXPECTED = {
    "range_1_avg_pmba": 1.00,
    "range_1_avg_sp": 0.50,
    "range_2_avg_pmba": 0.43,
    "range_2_avg_sp": -0.14,
    "range_3_avg_pmba": 0.20,
    "range_3_avg_sp": -0.60,
    "range_4_avg_pmba": -1.00,
    "range_4_avg_sp": 0.50,
    "total_score_pmba": 4,
    "total_score_sp": 0,
    "range12_mcnemar_p": 0.2500,
    "range12_wilcoxon_p": 0.1250,
    "range12_ttest_p": 0.0408,
    "range123_mcnemar_p": 0.1250,
    "range123_wilcoxon_p": 0.0625,
    "range123_ttest_p": 0.0277,
    "all_mcnemar_p": 0.7539,
    "all_wilcoxon_p": 0.3770,
    "all_ttest_p": 0.2704,
}

# Table: Robustness Check (tab:rob1)
ROBUSTNESS_EXPECTED = {
    2: {"ols_iv_c": 1, "cls_iv_c": 2, "ols_iv_nc": 1, "cls_iv_nc": 2, "ols_noiv_c": 2, "cls_noiv_c": 2, "majority": 1},
    11: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 4, "majority": 1},
    17: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    18: {"ols_iv_c": 2, "cls_iv_c": 2, "ols_iv_nc": 2, "cls_iv_nc": 2, "ols_noiv_c": 3, "cls_noiv_c": 4, "majority": 3},
    7: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 3, "cls_noiv_c": 1, "majority": 1},
    8: {"ols_iv_c": 3, "cls_iv_c": 2, "ols_iv_nc": 3, "cls_iv_nc": 2, "ols_noiv_c": 3, "cls_noiv_c": 1, "majority": 1},
    9: {"ols_iv_c": 1, "cls_iv_c": 4, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 4, "cls_noiv_c": 4, "majority": 1},
    10: {"ols_iv_c": 4, "cls_iv_c": 4, "ols_iv_nc": 4, "cls_iv_nc": 4, "ols_noiv_c": 2, "cls_noiv_c": 2, "majority": 1},
    13: {"ols_iv_c": 2, "cls_iv_c": 2, "ols_iv_nc": 2, "cls_iv_nc": 2, "ols_noiv_c": 3, "cls_noiv_c": 4, "majority": 1},
    15: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    19: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    1: {"ols_iv_c": 3, "cls_iv_c": 4, "ols_iv_nc": 3, "cls_iv_nc": 3, "ols_noiv_c": 2, "cls_noiv_c": 4, "majority": 1},
    4: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 4, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    6: {"ols_iv_c": 4, "cls_iv_c": 4, "ols_iv_nc": 4, "cls_iv_nc": 4, "ols_noiv_c": 2, "cls_noiv_c": 2, "majority": 1},
    12: {"ols_iv_c": 4, "cls_iv_c": 4, "ols_iv_nc": 4, "cls_iv_nc": 4, "ols_noiv_c": 2, "cls_noiv_c": 4, "majority": 2},
    14: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    3: {"ols_iv_c": 2, "cls_iv_c": 3, "ols_iv_nc": 2, "cls_iv_nc": 3, "ols_noiv_c": 3, "cls_noiv_c": 4, "majority": 1},
    5: {"ols_iv_c": 1, "cls_iv_c": 1, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 1, "cls_noiv_c": 1, "majority": 1},
    16: {"ols_iv_c": 1, "cls_iv_c": 4, "ols_iv_nc": 1, "cls_iv_nc": 3, "ols_noiv_c": 2, "cls_noiv_c": 4, "majority": 1},
    20: {"ols_iv_c": 1, "cls_iv_c": 4, "ols_iv_nc": 1, "cls_iv_nc": 1, "ols_noiv_c": 2, "cls_noiv_c": 2, "majority": 1},
}

ROBUSTNESS_SUMMARY_EXPECTED = {
    "range_1": {"ols_iv_c": 0.25, "cls_iv_c": 0.50, "ols_iv_nc": 0.25, "cls_iv_nc": 0.50, "ols_noiv_c": 0.75, "cls_noiv_c": 1.75, "majority": 0.50},
    "range_2": {"ols_iv_c": 1.00, "cls_iv_c": 1.00, "ols_iv_nc": 1.00, "cls_iv_nc": 0.86, "ols_noiv_c": 1.00, "cls_noiv_c": 1.14, "majority": 1.00},
    "range_3": {"ols_iv_c": 1.20, "cls_iv_c": 1.40, "ols_iv_nc": 1.20, "cls_iv_nc": 1.00, "ols_noiv_c": 1.40, "cls_noiv_c": 1.40, "majority": 1.80},
    "range_4": {"ols_iv_c": 2.75, "cls_iv_c": 1.00, "ols_iv_nc": 2.75, "cls_iv_nc": 2.00, "ols_noiv_c": 2.00, "cls_noiv_c": 1.25, "majority": 3.00},
    "paired_t_p": {"ols_iv_c": 0.0481, "cls_iv_c": 0.0331, "ols_iv_nc": 0.0481, "cls_iv_nc": 0.0176, "ols_noiv_c": 0.0675, "cls_noiv_c": 0.3123},
}

# Table: SP replication (tab:sp_replication)
SP_REPLICATION_EXPECTED = {
    2: {"n_obs": 103, "mu12_pct": 68.73, "alpha12_pct": 69.93, "sp_group": "3&4", "p_value": 0.3139},
    11: {"n_obs": 99, "mu12_pct": 63.32, "alpha12_pct": 62.52, "sp_group": "1&2", "p_value": 0.3973},
    17: {"n_obs": 94, "mu12_pct": 80.10, "alpha12_pct": 77.34, "sp_group": "1&2", "p_value": 0.1251},
    18: {"n_obs": 99, "mu12_pct": 48.74, "alpha12_pct": 45.84, "sp_group": "1&2", "p_value": 0.1577},
    7: {"n_obs": 97, "mu12_pct": 77.27, "alpha12_pct": 78.16, "sp_group": "3&4", "p_value": 0.3506},
    8: {"n_obs": 96, "mu12_pct": 65.39, "alpha12_pct": 66.99, "sp_group": "3&4", "p_value": 0.2805},
    9: {"n_obs": 93, "mu12_pct": 65.03, "alpha12_pct": 60.72, "sp_group": "1&2", "p_value": 0.0864},
    10: {"n_obs": 97, "mu12_pct": 75.25, "alpha12_pct": 75.73, "sp_group": "3&4", "p_value": 0.4268},
    13: {"n_obs": 102, "mu12_pct": 59.95, "alpha12_pct": 61.73, "sp_group": "3&4", "p_value": 0.2943},
    15: {"n_obs": 100, "mu12_pct": 75.48, "alpha12_pct": 70.10, "sp_group": "1&2", "p_value": 0.0254},
    19: {"n_obs": 104, "mu12_pct": 77.39, "alpha12_pct": 73.41, "sp_group": "1&2", "p_value": 0.0713},
    1: {"n_obs": 102, "mu12_pct": 65.93, "alpha12_pct": 64.62, "sp_group": "1&2", "p_value": 0.3261},
    4: {"n_obs": 100, "mu12_pct": 73.74, "alpha12_pct": 75.15, "sp_group": "3&4", "p_value": 0.2875},
    6: {"n_obs": 100, "mu12_pct": 72.64, "alpha12_pct": 72.36, "sp_group": "1&2", "p_value": 0.4562},
    12: {"n_obs": 101, "mu12_pct": 56.52, "alpha12_pct": 51.82, "sp_group": "1&2", "p_value": 0.0586},
    14: {"n_obs": 98, "mu12_pct": 80.86, "alpha12_pct": 80.41, "sp_group": "1&2", "p_value": 0.4291},
    3: {"n_obs": 101, "mu12_pct": 54.24, "alpha12_pct": 57.20, "sp_group": "3&4", "p_value": 0.1874},
    5: {"n_obs": 101, "mu12_pct": 77.07, "alpha12_pct": 77.17, "sp_group": "3&4", "p_value": 0.4839},
    16: {"n_obs": 100, "mu12_pct": 72.01, "alpha12_pct": 74.99, "sp_group": "3&4", "p_value": 0.1236},
    20: {"n_obs": 103, "mu12_pct": 64.76, "alpha12_pct": 62.74, "sp_group": "1&2", "p_value": 0.2470},
}
