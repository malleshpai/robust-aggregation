"""Numbers printed in the FINAL paper (paper/main.tex), transcribed by hand.

Each block cites the LaTeX label (or section/paragraph) it comes from.  Values
are written exactly as printed.  ``expected_values()`` turns them into a flat
dict ``{key: (value, decimals)}`` whose keys match ``final_paper.flat_values``;
``decimals`` is the number of decimals printed in the paper (None = exact match
for integers, strings and booleans).

This module is the only place the paper's numbers live; the check never reads
files outside Replication/ at run time.
"""
from __future__ import annotations

PAPER_NFT_ORDER = [2, 11, 17, 18, 7, 8, 9, 10, 13, 15, 19, 1, 4, 6, 12, 14, 3, 5, 16, 20]

# ---------------------------------------------------------------------------
# Section 4.1-4.2 (Experimental design, PMBA implementation)
# ---------------------------------------------------------------------------
SAMPLE = {
    "participants": 199,             # "A total of 199 eligible responses"
    "nfts_per_participant": 10,      # "For each participant, 10 NFTs from a pool of 20"
    "n_min": 93, "n_max": 104,       # "(93 to 104 per NFT)"
    "dropped_pairs": 6,              # "This removes six participant--NFT pairs in total"
    "F_min": 0.23, "F_max": 3.96,    # "first-stage joint F statistics range from 0.23 to 3.96"
}

# ---------------------------------------------------------------------------
# Table tab:prediction_errors (Section 4.3.1)
# ---------------------------------------------------------------------------
PREDICTION_ERRORS = {
    # method: (MAE, exact out of 20, PMBA minus method, one-sided paired t p)
    "pmba": (1.25, 5, None, None),
    "mean_mu": (1.50, 3, -0.25, 0.0481),
    "mean_alpha": (1.40, 5, -0.15, 0.1896),
    "vote": (1.55, 3, -0.30, 0.0276),
}
# "The gains are 0.15 to 0.30 categories, i.e. 11--19% of the benchmarks' MAE."
GAINS_TEXT = {"gain_min": 0.15, "gain_max": 0.30, "gain_share_min_pct": 11, "gain_share_max_pct": 19}

# Paragraph "Uncertainty."
UNCERTAINTY = {
    "ci95_vs_mean_mu": (-0.55, 0.05),
    "ci95_vs_mean_alpha": (-0.50, 0.20),
    "p_paired_t_vs_mean_mu": 0.0481,
    "p_signed_rank_vs_mean_mu": 0.0938,
}

# Paragraph "Where does the difference come from?"
WHERE = {
    "improved": 5, "unchanged": 14, "worse": 1,
    "improved_items": "1,3,6,13,18",
    "raised_above_range1_items": "1,3,6,13",
    "lowered_overprediction_items": "18",
    "worse_items": "10",
}

# ---------------------------------------------------------------------------
# Table tab:true_range (Section 4.3.1); same numbers in the summary rows of tab:item_predictions
# ---------------------------------------------------------------------------
TRUE_RANGE = {
    # range: (items, {method: (MAE, exact)})
    "1": (4, {"pmba": (0.25, 3), "mean_mu": (0.50, 3), "mean_alpha": (0.50, 3), "vote": (0.50, 3)}),
    "2": (7, {"pmba": (1.00, 1), "mean_mu": (1.00, 0), "mean_alpha": (0.86, 1), "vote": (1.00, 0)}),
    "3": (5, {"pmba": (1.20, 1), "mean_mu": (1.80, 0), "mean_alpha": (1.60, 1), "vote": (2.00, 0)}),
    "4": (4, {"pmba": (2.75, 0), "mean_mu": (3.00, 0), "mean_alpha": (3.00, 0), "vote": (3.00, 0)}),
    "all": (20, {"pmba": (1.25, 5), "mean_mu": (1.50, 3), "mean_alpha": (1.40, 5), "vote": (1.55, 3)}),
}

# "Predicting Range 2 on every item would have MAE 0.85 and seven exact predictions ...
#  never off by more than two categories."
CONSTANT_RANGE2 = {"mae": 0.85, "exact": 7, "max_error": 2}

# Section 4.3.2: "PMBA is correct on 12 of 20 items ... compared with 10 for SP ... p=0.7539"
SP_TEXT = {"pmba_correct": 12, "sp_correct": 10, "mcnemar_p": 0.7539}

# Section 4.4 Discussion: "all three benchmarks predict Range 1 for every Range 4 item"
DISCUSSION = {"benchmarks_predict_1_for_all_range4": True}

# Paragraph "Validity of the estimated state-contingent means" (Section 4.4)
VALIDITY = {
    "n_components": 320, "n_negative": 94, "n_above_one": 18, "n_within": 208,
    "share_within_pct": 65,
    "selected_out_of_bounds": 17,
    # "In every specification, PMBA has a lower MAE than the mean-belief rules and plurality voting."
    "pmba_specs_beat_all_benchmarks_on_mae": True,
    # "The valid-coordinate specifications also make more exact predictions (7 or 8 of 20, against at most 5)"
    "valid_coordinate_exact_min": 7, "valid_coordinate_exact_max": 8,
    "baseline_and_benchmarks_exact_max": 5,
    # "matching on coordinate 1 or 4 alone makes fewer exact predictions than the mean
    #  second-order belief rule (4 and 3 of 20, against 5)"
    "coord_1_exact": 4, "coord_4_exact": 3, "mean_alpha_exact": 5,
}

# ---------------------------------------------------------------------------
# Table tab:item_predictions (Appendix F.1)
# ---------------------------------------------------------------------------
ITEM_PREDICTIONS = {
    # nft: (true, PMBA, Mean mu, Mean alpha, Voting, |err| PMBA, Mean mu, Mean alpha, Voting)
    2: (1, 1, 1, 1, 1, 0, 0, 0, 0),
    11: (1, 1, 1, 1, 1, 0, 0, 0, 0),
    17: (1, 1, 1, 1, 1, 0, 0, 0, 0),
    18: (1, 2, 3, 3, 3, 1, 2, 2, 2),
    7: (2, 1, 1, 1, 1, 1, 1, 1, 1),
    8: (2, 3, 1, 2, 1, 1, 1, 0, 1),
    9: (2, 1, 1, 1, 1, 1, 1, 1, 1),
    10: (2, 4, 1, 1, 1, 2, 1, 1, 1),
    13: (2, 2, 1, 1, 1, 0, 1, 1, 1),
    15: (2, 1, 1, 1, 1, 1, 1, 1, 1),
    19: (2, 1, 1, 1, 1, 1, 1, 1, 1),
    1: (3, 3, 1, 1, 1, 0, 2, 2, 2),
    4: (3, 1, 1, 1, 1, 2, 2, 2, 2),
    6: (3, 4, 1, 1, 1, 1, 2, 2, 2),
    12: (3, 4, 2, 3, 1, 1, 1, 0, 2),
    14: (3, 1, 1, 1, 1, 2, 2, 2, 2),
    3: (4, 2, 1, 1, 1, 2, 3, 3, 3),
    5: (4, 1, 1, 1, 1, 3, 3, 3, 3),
    16: (4, 1, 1, 1, 1, 3, 3, 3, 3),
    20: (4, 1, 1, 1, 1, 3, 3, 3, 3),
}
# subset: {benchmark: (Wilcoxon exact p, paired t p)}, one-sided favouring PMBA
ITEM_SUBGROUP_TESTS = {
    "range12": {"mean_mu": (0.5000, 0.2942), "mean_alpha": (0.6875, 0.5000), "vote": (0.5000, 0.2942)},
    "range123": {"mean_mu": (0.1562, 0.0819), "mean_alpha": (0.3828, 0.2722), "vote": (0.0938, 0.0481)},
    "all": {"mean_mu": (0.0938, 0.0481), "mean_alpha": (0.2812, 0.1896), "vote": (0.0547, 0.0276)},
}

# ---------------------------------------------------------------------------
# Table tab:score_comparison (Appendix F.1)
# ---------------------------------------------------------------------------
SCORE_COMPARISON = {
    # nft: (true group, PMBA group, PMBA four-state prediction, SP group, PMBA score, SP score)
    2: ("1&2", "1&2", 1, "3&4", 1, -1),
    11: ("1&2", "1&2", 1, "1&2", 1, 1),
    17: ("1&2", "1&2", 1, "1&2", 1, 1),
    18: ("1&2", "1&2", 2, "1&2", 1, 1),
    7: ("1&2", "1&2", 1, "3&4", 1, -1),
    8: ("1&2", "3&4", 3, "3&4", -1, -1),
    9: ("1&2", "1&2", 1, "1&2", 1, 1),
    10: ("1&2", "3&4", 4, "3&4", -1, -1),
    13: ("1&2", "1&2", 2, "3&4", 1, -1),
    15: ("1&2", "1&2", 1, "1&2", 1, 1),
    19: ("1&2", "1&2", 1, "1&2", 1, 1),
    1: ("3&4", "3&4", 3, "1&2", 1, -1),
    4: ("3&4", "1&2", 1, "3&4", -1, 1),
    6: ("3&4", "3&4", 4, "1&2", 1, -1),
    12: ("3&4", "3&4", 4, "1&2", 1, -1),
    14: ("3&4", "1&2", 1, "1&2", -1, -1),
    3: ("3&4", "1&2", 2, "3&4", -1, 1),
    5: ("3&4", "1&2", 1, "3&4", -1, 1),
    16: ("3&4", "1&2", 1, "3&4", -1, 1),
    20: ("3&4", "1&2", 1, "1&2", -1, -1),
}
SCORE_RANGE_AVG = {"1": (1.00, 0.50), "2": (0.43, -0.14), "3": (0.20, -0.60), "4": (-1.00, 0.50)}
SCORE_TOTALS = (4, 0)
# subset: (McNemar exact p, Wilcoxon exact p, paired t p)
SCORE_TESTS = {
    "range12": (0.2500, 0.1250, 0.0408),
    "range123": (0.1250, 0.0625, 0.0277),
    "all": (0.7539, 0.3770, 0.2704),
}

# ---------------------------------------------------------------------------
# Figure fig:state_mean_distribution (State_contingent_Vec_dist.png)
# Read from the image: legend counts/shares, panel (b) vector count, and the
# bar heights of panel (a) (bins of width 0.2 aligned at 0; key = left edge).
# ---------------------------------------------------------------------------
FIG_DISTRIBUTION = {
    "n_vectors": 80, "all_sums_one": True,
    "n_negative": 94, "n_within": 208, "n_above_one": 18,
    "share_negative_pct": 29.4, "share_within_pct": 65.0, "share_above_pct": 5.6,
}
FIG_DISTRIBUTION_BINS = {
    -2.2: 1, -1.6: 1, -1.2: 3, -1.0: 2, -0.8: 1, -0.6: 10, -0.4: 22, -0.2: 54,
    0.0: 74, 0.2: 45, 0.4: 32, 0.6: 33, 0.8: 24,
    1.0: 11, 1.2: 3, 1.4: 2, 1.6: 1, 3.6: 1,
}

# ---------------------------------------------------------------------------
# Figure validity (valid_grid.png), read cell by cell from the image.
# Per NFT: 16 cells = candidate state 1..4, each with coordinates 1..4.
# N = below 0 (red), V = within [0,1] (grey), A = above 1 (orange).
# ---------------------------------------------------------------------------
FIG_VALID_GRID = {
    2: "VVVN" "VVNV" "NNAN" "VVNA",
    11: "VVVN" "VVVV" "VVVV" "VNVV",
    17: "VNVV" "VVVN" "NVVV" "VVNV",
    18: "VVNN" "VVVN" "NVVV" "NNVV",
    7: "VVVN" "VVNN" "VVVV" "NNVA",
    8: "VNVN" "NVNV" "VVNV" "NNAV",
    9: "VVVV" "VAVN" "VNVV" "NVVV",
    10: "ANVV" "VVNN" "NVAV" "VVNV",
    13: "VVNV" "VVVV" "VVVV" "NVVV",
    15: "VVNN" "VVVV" "VVVN" "NAVV",
    19: "VVNV" "NVVN" "VVVN" "VVVV",
    1: "VVVN" "VVNV" "VVVV" "NNVV",
    4: "VVVN" "NVVV" "NVVV" "ANVV",
    6: "ANVV" "NVVV" "NVVV" "VVNV",
    12: "VNVN" "NANV" "VNAN" "VNVV",
    14: "AVNN" "VANN" "NNAV" "VVNV",
    3: "VVNN" "NVVV" "VVVN" "NNVA",
    5: "VVNV" "VVVN" "NVVV" "VNVV",
    16: "ANVN" "VVVN" "VVNV" "NVVV",
    20: "VVVN" "NAVV" "VNVN" "NVVV",
}

# ---------------------------------------------------------------------------
# Table alternative-matching (Appendix F.2, landscape)
# Columns: Baseline OLS-IV, d=1, d=2, d=3, d=4, Own>=1, Own>=2, Own>=3, Mean mu, Mean alpha, Vote
# ---------------------------------------------------------------------------
ALT_COLUMNS = ["pmba", "coord_1", "coord_2", "coord_3", "coord_4",
               "own_ge_1", "own_ge_2", "own_ge_3", "mean_mu", "mean_alpha", "vote"]
ALT_MATCHING = {
    2: (1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    11: (1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1),
    17: (1, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1),
    18: (2, 4, 3, 4, 3, 2, 2, 2, 3, 3, 3),
    7: (1, 2, 3, 1, 3, 1, 1, 1, 1, 1, 1),
    8: (3, 3, 1, 1, 3, 4, 1, 3, 1, 2, 1),
    9: (1, 3, 4, 2, 1, 2, 2, 1, 1, 1, 1),
    10: (4, 4, 3, 1, 1, 1, 1, 4, 1, 1, 1),
    13: (2, 2, 4, 4, 3, 2, 2, 2, 1, 1, 1),
    15: (1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1),
    19: (1, 3, 4, 4, 1, 1, 1, 1, 1, 1, 1),
    1: (3, 3, 3, 1, 2, 3, 3, 3, 1, 1, 1),
    4: (1, 1, 1, 2, 3, 1, 1, 1, 1, 1, 1),
    6: (4, 4, 3, 2, 2, 1, 1, 4, 1, 1, 1),
    12: (4, 4, 4, 4, 4, 3, 4, 4, 2, 3, 1),
    14: (1, 2, 1, 1, 2, 1, 4, 4, 1, 1, 1),
    3: (2, 3, 2, 4, 2, 4, 2, 2, 1, 1, 1),
    5: (1, 2, 3, 2, 1, 1, 1, 1, 1, 1, 1),
    16: (1, 3, 3, 1, 2, 1, 4, 4, 1, 1, 1),
    20: (1, 3, 4, 4, 2, 2, 2, 1, 1, 1, 1),
}
# state: (correct counts per column, MAE per column)
ALT_SUMMARY = {
    "1": ((3, 0, 2, 2, 2, 3, 3, 3, 3, 3, 3),
          (0.25, 2.50, 1.00, 1.00, 0.75, 0.25, 0.25, 0.25, 0.50, 0.50, 0.50)),
    "2": ((1, 3, 0, 2, 0, 2, 2, 2, 0, 1, 0),
          (1.00, 0.71, 1.43, 1.00, 1.00, 0.86, 0.71, 0.86, 1.00, 0.86, 1.00)),
    "3": ((1, 1, 2, 0, 1, 2, 1, 1, 0, 1, 0),
          (1.20, 1.00, 1.00, 1.40, 0.80, 1.20, 1.20, 1.00, 1.80, 1.60, 2.00)),
    "4": ((0, 0, 1, 2, 0, 1, 1, 1, 0, 0, 0),
          (2.75, 1.25, 1.00, 1.25, 2.25, 2.00, 1.75, 2.00, 3.00, 3.00, 3.00)),
    "all": ((5, 4, 5, 6, 3, 8, 7, 7, 3, 5, 3),
            (1.25, 1.25, 1.15, 1.15, 1.15, 1.05, 0.95, 1.00, 1.50, 1.40, 1.55)),
}
# Table note: "Under Own >= 4 some NFTs have no eligible candidate, so that column is omitted."
ALT_OWN_GE_4_HAS_NFT_WITHOUT_CANDIDATE = True

# ---------------------------------------------------------------------------
# Table tab:rob1 (Appendix F, Robustness checks)
# Columns: OLS-IV c, CLS-IV c, OLS-IV nc, CLS-IV nc, OLS no-IV c, CLS no-IV c, Mean belief
# ---------------------------------------------------------------------------
ROB_COLUMNS = ["ols_iv_c", "cls_iv_c", "ols_iv_nc", "cls_iv_nc", "ols_noiv_c", "cls_noiv_c", "mean_mu"]
ROBUSTNESS = {
    2: (1, 2, 1, 2, 2, 2, 1),
    11: (1, 1, 1, 1, 1, 4, 1),
    17: (1, 1, 1, 1, 1, 1, 1),
    18: (2, 2, 2, 2, 3, 4, 3),
    7: (1, 1, 1, 1, 3, 1, 1),
    8: (3, 2, 3, 2, 3, 1, 1),
    9: (1, 4, 1, 1, 4, 4, 1),
    10: (4, 4, 4, 4, 2, 2, 1),
    13: (2, 2, 2, 2, 3, 4, 1),
    15: (1, 1, 1, 1, 1, 1, 1),
    19: (1, 1, 1, 1, 1, 1, 1),
    1: (3, 4, 3, 3, 2, 4, 1),
    4: (1, 1, 1, 4, 1, 1, 1),
    6: (4, 4, 4, 4, 2, 2, 1),
    12: (4, 4, 4, 4, 2, 4, 2),
    14: (1, 1, 1, 1, 1, 1, 1),
    3: (2, 3, 2, 3, 3, 4, 1),
    5: (1, 1, 1, 1, 1, 1, 1),
    16: (1, 4, 1, 3, 2, 4, 1),
    20: (1, 4, 1, 1, 2, 2, 1),
}
ROBUSTNESS_MAE = {
    "1": (0.25, 0.50, 0.25, 0.50, 0.75, 1.75, 0.50),
    "2": (1.00, 1.00, 1.00, 0.86, 1.00, 1.14, 1.00),
    "3": (1.20, 1.40, 1.20, 1.00, 1.40, 1.40, 1.80),
    "4": (2.75, 1.00, 2.75, 2.00, 2.00, 1.25, 3.00),
}
ROBUSTNESS_P = (0.0481, 0.0331, 0.0481, 0.0176, 0.0675, 0.3123)
# Note: "OLS-IV with intercept and OLS-IV without intercept produce identical state predictions"
ROBUSTNESS_OLS_C_EQUALS_NC = True

# ---------------------------------------------------------------------------
# Table tab:firststage (Appendix F, First-stage fit)
# ---------------------------------------------------------------------------
FIRST_STAGE = {
    # nft: (n, retained, F range 1, F range 2, F range 3)
    1: (102, 102, 1.77, 2.67, 1.55),
    2: (103, 103, 2.31, 1.31, 2.18),
    3: (101, 101, 0.68, 1.81, 1.16),
    4: (100, 99, 2.10, 3.50, 1.36),
    5: (101, 101, 0.87, 1.45, 0.29),
    6: (100, 100, 1.13, 0.90, 0.98),
    7: (97, 97, 1.25, 1.36, 0.81),
    8: (96, 95, 1.08, 0.23, 0.84),
    9: (93, 93, 1.74, 1.09, 1.62),
    10: (97, 95, 0.45, 0.43, 1.23),
    11: (99, 98, 3.96, 0.89, 1.93),
    12: (101, 101, 1.51, 0.40, 2.57),
    13: (102, 102, 1.23, 1.14, 0.89),
    14: (98, 97, 1.21, 1.19, 0.94),
    15: (100, 100, 3.52, 1.09, 2.95),
    16: (100, 100, 0.36, 0.95, 0.60),
    17: (94, 94, 0.84, 1.39, 0.66),
    18: (99, 99, 0.81, 1.18, 0.49),
    19: (104, 104, 0.50, 0.72, 0.54),
    20: (103, 103, 0.90, 2.22, 0.37),
}
FIRST_STAGE_COUNT = 60      # "All 60 statistics are below 10."
FIRST_STAGE_BELOW_10 = 60

# ---------------------------------------------------------------------------
# Table tab:nft_list (Appendix F, NFTs used in the experiment)
# ---------------------------------------------------------------------------
NFT_LIST = {
    # id: (price ETH, price SGD, range)
    1: (4, 10102.96, 3),
    2: (0.0003, 0.76, 1),
    3: (13, 32834.62, 4),
    4: (6, 15154.44, 3),
    5: (39, 98503.86, 4),
    6: (3.4899, 8814.58, 3),
    7: (0.31, 782.98, 2),
    8: (1.65, 4167.47, 2),
    9: (1.27, 3207.69, 2),
    10: (1.089, 2750.53, 2),
    11: (0.0758, 191.45, 1),
    12: (3.5, 8840.09, 3),
    13: (2.159, 5453.07, 2),
    14: (4.49, 11340.57, 3),
    15: (1.05, 2652.03, 2),
    16: (9.88, 24954.31, 4),
    17: (0.017, 42.94, 1),
    18: (0.0455, 114.92, 1),
    19: (1.62, 4091.70, 2),
    20: (25, 63143.50, 4),
}
# Range bounds in SGD (Section 4.1 and the table note).
RANGE_BOUNDS_SGD = {1: (0, 250), 2: (250, 7500), 3: (7500, 21500), 4: (21500, float("inf"))}

# ---------------------------------------------------------------------------
# Table tab:sp_replication (Appendix F, Replication of SP)
# ---------------------------------------------------------------------------
SP_REPLICATION = {
    # nft: (N, mu_(1&2) %, mean alpha_(1&2) %, SP prediction, one-sided p)
    2: (103, 68.73, 69.93, "3&4", 0.3139),
    11: (99, 63.32, 62.52, "1&2", 0.3973),
    17: (94, 80.10, 77.34, "1&2", 0.1251),
    18: (99, 48.74, 45.84, "1&2", 0.1577),
    7: (97, 77.27, 78.16, "3&4", 0.3506),
    8: (96, 65.39, 66.99, "3&4", 0.2805),
    9: (93, 65.03, 60.72, "1&2", 0.0864),
    10: (97, 75.25, 75.73, "3&4", 0.4268),
    13: (102, 59.95, 61.73, "3&4", 0.2943),
    15: (100, 75.48, 70.10, "1&2", 0.0254),
    19: (104, 77.39, 73.41, "1&2", 0.0713),
    1: (102, 65.93, 64.62, "1&2", 0.3261),
    4: (100, 73.74, 75.15, "3&4", 0.2875),
    6: (100, 72.64, 72.36, "1&2", 0.4562),
    12: (101, 56.52, 51.82, "1&2", 0.0586),
    14: (98, 80.86, 80.41, "1&2", 0.4291),
    3: (101, 54.24, 57.20, "3&4", 0.1874),
    5: (101, 77.07, 77.17, "3&4", 0.4839),
    16: (100, 72.01, 74.99, "3&4", 0.1236),
    20: (103, 64.76, 62.74, "1&2", 0.2470),
}


def expected_values() -> dict:
    """Flatten the blocks above into {key: (value, decimals)} matching final_paper.flat_values."""
    e = {}

    e["sec4:sample/participants"] = (SAMPLE["participants"], None)
    e["sec4:sample/nfts_per_participant_min"] = (SAMPLE["nfts_per_participant"], None)
    e["sec4:sample/nfts_per_participant_max"] = (SAMPLE["nfts_per_participant"], None)
    e["sec4:implementation/n_min"] = (SAMPLE["n_min"], None)
    e["sec4:implementation/n_max"] = (SAMPLE["n_max"], None)
    e["sec4:implementation/dropped_pairs"] = (SAMPLE["dropped_pairs"], None)
    e["sec4:implementation/F_min"] = (SAMPLE["F_min"], 2)
    e["sec4:implementation/F_max"] = (SAMPLE["F_max"], 2)
    e["tab:firststage/F_count"] = (FIRST_STAGE_COUNT, None)
    e["tab:firststage/F_below_10"] = (FIRST_STAGE_BELOW_10, None)
    for nft, (n, retained, f1, f2, f3) in FIRST_STAGE.items():
        e[f"tab:firststage/nft{nft}/n"] = (n, None)
        e[f"tab:firststage/nft{nft}/retained"] = (retained, None)
        for d, f in enumerate((f1, f2, f3), start=1):
            e[f"tab:firststage/nft{nft}/F_range{d}"] = (f, 2)

    for m, (mae, exact, diff, p) in PREDICTION_ERRORS.items():
        e[f"tab:prediction_errors/{m}/mae"] = (mae, 2)
        e[f"tab:prediction_errors/{m}/exact"] = (exact, None)
        if diff is not None:
            e[f"tab:prediction_errors/{m}/pmba_minus_method"] = (diff, 2)
            e[f"tab:prediction_errors/{m}/p_paired_t"] = (p, 4)
    e["sec4:results/gain_min"] = (GAINS_TEXT["gain_min"], 2)
    e["sec4:results/gain_max"] = (GAINS_TEXT["gain_max"], 2)
    e["sec4:results/gain_share_min_pct"] = (GAINS_TEXT["gain_share_min_pct"], 0)
    e["sec4:results/gain_share_max_pct"] = (GAINS_TEXT["gain_share_max_pct"], 0)

    e["sec4:uncertainty/ci95_vs_mean_mu_lo"] = (UNCERTAINTY["ci95_vs_mean_mu"][0], 2)
    e["sec4:uncertainty/ci95_vs_mean_mu_hi"] = (UNCERTAINTY["ci95_vs_mean_mu"][1], 2)
    e["sec4:uncertainty/ci95_vs_mean_alpha_lo"] = (UNCERTAINTY["ci95_vs_mean_alpha"][0], 2)
    e["sec4:uncertainty/ci95_vs_mean_alpha_hi"] = (UNCERTAINTY["ci95_vs_mean_alpha"][1], 2)
    e["sec4:uncertainty/p_paired_t_vs_mean_mu"] = (UNCERTAINTY["p_paired_t_vs_mean_mu"], 4)
    e["sec4:uncertainty/p_signed_rank_vs_mean_mu"] = (UNCERTAINTY["p_signed_rank_vs_mean_mu"], 4)
    for k, val in WHERE.items():
        e[f"sec4:where/{k}"] = (val, None)
    e["sec4:discussion/benchmarks_predict_1_for_all_range4"] = (DISCUSSION["benchmarks_predict_1_for_all_range4"], None)

    for label in ("tab:true_range", "tab:item_predictions"):
        for rng, (n_items, by_m) in TRUE_RANGE.items():
            e[f"{label}/range{rng}/items"] = (n_items, None)
            for m, (mae, exact) in by_m.items():
                e[f"{label}/range{rng}/{m}/mae"] = (mae, 2)
                e[f"{label}/range{rng}/{m}/exact"] = (exact, None)

    e["sec4:constant_range2/mae"] = (CONSTANT_RANGE2["mae"], 2)
    e["sec4:constant_range2/exact"] = (CONSTANT_RANGE2["exact"], None)
    e["sec4:constant_range2/max_error"] = (CONSTANT_RANGE2["max_error"], None)

    methods = ["pmba", "mean_mu", "mean_alpha", "vote"]
    for nft, row in ITEM_PREDICTIONS.items():
        preds, errs = row[1:5], row[5:9]
        for m, p, err in zip(methods, preds, errs):
            e[f"tab:item_predictions/nft{nft}/{m}"] = (p, None)
            e[f"tab:item_predictions/nft{nft}/{m}_abs_error"] = (err, None)
    for subset, by_m in ITEM_SUBGROUP_TESTS.items():
        for m, (w, t) in by_m.items():
            e[f"tab:item_predictions/{subset}/{m}/wilcoxon_p"] = (w, 4)
            e[f"tab:item_predictions/{subset}/{m}/t_p"] = (t, 4)

    e["sec4:sp/pmba_correct"] = (SP_TEXT["pmba_correct"], None)
    e["sec4:sp/sp_correct"] = (SP_TEXT["sp_correct"], None)
    e["sec4:sp/mcnemar_p"] = (SP_TEXT["mcnemar_p"], 4)
    fields = ("true_group", "pmba_group", "pmba_pred", "sp_group", "pmba_score", "sp_score")
    for nft, row in SCORE_COMPARISON.items():
        for field, val in zip(fields, row):
            e[f"tab:score_comparison/nft{nft}/{field}"] = (val, None)
    for rng, (a_pmba, a_sp) in SCORE_RANGE_AVG.items():
        e[f"tab:score_comparison/range{rng}/avg_pmba"] = (a_pmba, 2)
        e[f"tab:score_comparison/range{rng}/avg_sp"] = (a_sp, 2)
    e["tab:score_comparison/total_pmba"] = (SCORE_TOTALS[0], None)
    e["tab:score_comparison/total_sp"] = (SCORE_TOTALS[1], None)
    for subset, (mc, w, t) in SCORE_TESTS.items():
        e[f"tab:score_comparison/{subset}/mcnemar_p"] = (mc, 4)
        e[f"tab:score_comparison/{subset}/wilcoxon_p"] = (w, 4)
        e[f"tab:score_comparison/{subset}/t_p"] = (t, 4)

    for k in ("n_components", "n_negative", "n_above_one", "n_within", "selected_out_of_bounds",
              "pmba_specs_beat_all_benchmarks_on_mae", "valid_coordinate_exact_min",
              "valid_coordinate_exact_max", "baseline_and_benchmarks_exact_max",
              "coord_1_exact", "coord_4_exact", "mean_alpha_exact"):
        e[f"sec4:validity/{k}"] = (VALIDITY[k], None)
    e["sec4:validity/share_within_pct"] = (VALIDITY["share_within_pct"], 0)

    for k, val in FIG_DISTRIBUTION.items():
        decimals = 1 if k.endswith("_pct") else None
        e[f"fig:state_mean_distribution/{k}"] = (val, decimals)
    for left, count in FIG_DISTRIBUTION_BINS.items():
        e[f"fig:state_mean_distribution/bin_{left:+.1f}"] = (count, None)
    for nft, cells in FIG_VALID_GRID.items():
        e[f"fig:validity/nft{nft}"] = (cells, None)

    for nft, row in ALT_MATCHING.items():
        for m, val in zip(ALT_COLUMNS, row):
            e[f"alternative-matching/nft{nft}/{m}"] = (val, None)
    for state, (correct, mae) in ALT_SUMMARY.items():
        for m, c, a in zip(ALT_COLUMNS, correct, mae):
            e[f"alternative-matching/state{state}/{m}/exact"] = (c, None)
            e[f"alternative-matching/state{state}/{m}/mae"] = (a, 2)
    e["alternative-matching/own_ge_4_has_nft_without_candidate"] = (ALT_OWN_GE_4_HAS_NFT_WITHOUT_CANDIDATE, None)

    for nft, row in ROBUSTNESS.items():
        for m, val in zip(ROB_COLUMNS, row):
            e[f"tab:rob1/nft{nft}/{m}"] = (val, None)
    for rng, row in ROBUSTNESS_MAE.items():
        for m, val in zip(ROB_COLUMNS, row):
            e[f"tab:rob1/range{rng}/{m}/mae"] = (val, 2)
    for m, p in zip(ROB_COLUMNS, ROBUSTNESS_P):
        e[f"tab:rob1/p_paired_t/{m}"] = (p, 4)
    e["tab:rob1/ols_iv_c_equals_ols_iv_nc"] = (ROBUSTNESS_OLS_C_EQUALS_NC, None)

    for nft, (_eth, _sgd, rng) in NFT_LIST.items():
        e[f"tab:nft_list/nft{nft}/range"] = (rng, None)

    for nft, (n, mu12, a12, group, p) in SP_REPLICATION.items():
        e[f"tab:sp_replication/nft{nft}/n"] = (n, None)
        e[f"tab:sp_replication/nft{nft}/mu12_pct"] = (mu12, 2)
        e[f"tab:sp_replication/nft{nft}/alpha12_pct"] = (a12, 2)
        e[f"tab:sp_replication/nft{nft}/sp_group"] = (group, None)
        e[f"tab:sp_replication/nft{nft}/p_one_sided"] = (p, 4)

    return e


def nft_list_internal_checks() -> list:
    """Checks of tab:nft_list against itself (the prices are not in the raw data):
    each SGD price lies in its assigned range, and all prices use one ETH/SGD rate."""
    rate = NFT_LIST[1][1] / NFT_LIST[1][0]
    checks = []
    for nft, (eth, sgd, rng) in NFT_LIST.items():
        lo, hi = RANGE_BOUNDS_SGD[rng]
        checks.append((f"tab:nft_list/nft{nft}/sgd_price_in_range", lo <= sgd < hi))
        checks.append((f"tab:nft_list/nft{nft}/sgd_equals_eth_times_rate", abs(eth * rate - sgd) <= 0.011))
    return checks
