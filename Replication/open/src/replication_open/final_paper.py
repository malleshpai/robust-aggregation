"""Compute every empirical number reported in the final paper (paper/main.tex).

Everything starts from the raw data in Replication/data/raw/ and reuses the
panel construction in data_prep.py and the estimators in estimators.py.

Conventions used throughout (all taken from the paper):

* States, ranges and coordinates are numbered 1..4.
* The fitted state-contingent mean vectors of an NFT are stored in a 4x4
  array ``means`` with ``means[k-1, d-1]`` = coordinate d of state k.
* Every argmax / argmin selects the lowest index on exact ties
  (numpy's argmax/argmin already do this).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from .config import DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE, KEY_COLUMNS, L_STATES
from .data_prep import build_all_panels, filter_verified, load_raw_rows
from .estimators import estimate_by_method, estimate_ols
from .stats import mcnemar_exact_pvalue, wilcoxon_signed_rank_pvalue

# Order in which NFTs appear in the paper's item-level tables (grouped by true range).
PAPER_NFT_ORDER = [2, 11, 17, 18, 7, 8, 9, 10, 13, 15, 19, 1, 4, 6, 12, 14, 3, 5, 16, 20]

# The four-state methods compared in Section 4 (column order of tab:prediction_errors).
MAIN_METHODS = ["pmba", "mean_mu", "mean_alpha", "vote"]

# Columns of the alternative-matching table (Appendix table "alternative-matching").
ALT_METHODS = [
    "pmba", "coord_1", "coord_2", "coord_3", "coord_4",
    "own_ge_1", "own_ge_2", "own_ge_3", "mean_mu", "mean_alpha", "vote",
]

# Columns of the robustness table tab:rob1 (the last one is the mean first-order belief rule).
ROBUSTNESS_METHODS = ["ols_iv_c", "cls_iv_c", "ols_iv_nc", "cls_iv_nc", "ols_noiv_c", "cls_noiv_c"]

# Subsets of NFTs used for the subgroup tests in tab:item_predictions and tab:score_comparison.
SUBSETS = {"range12": (1, 2), "range123": (1, 2, 3), "all": (1, 2, 3, 4)}


# ---------------------------------------------------------------------------
# Prediction rules
# ---------------------------------------------------------------------------

def state_means_from_beta(all_beta: np.ndarray) -> np.ndarray:
    """estimators.py stores row d = regression for coordinate d; transpose to [state, coordinate]."""
    return all_beta.T.copy()


def nearest_state(means: np.ndarray, mu_hat: np.ndarray) -> int:
    """Rule (eq:state_rule): smallest k minimising the Euclidean distance to mu_hat."""
    distances = np.linalg.norm(means - mu_hat.reshape(1, -1), axis=1)
    return int(np.argmin(distances)) + 1


def one_coordinate_state(means: np.ndarray, mu_hat: np.ndarray, d: int) -> int:
    """Match on coordinate d alone, keeping out-of-range estimates."""
    gaps = np.abs(means[:, d - 1] - mu_hat[d - 1])
    return int(np.argmin(gaps)) + 1


def valid_mask(means: np.ndarray) -> np.ndarray:
    """True where an estimated component lies in [0, 1]."""
    return (means >= 0.0) & (means <= 1.0)


def own_valid_state(means: np.ndarray, mu_hat: np.ndarray, min_valid: int):
    """Candidate-specific valid-coordinate rule "Own >= min_valid".

    For each candidate state use only its coordinates in [0, 1]; the candidate is
    eligible if it has at least ``min_valid`` such coordinates and is scored by the
    root mean square of its gaps from mu_hat over those coordinates.  Returns None
    when no candidate is eligible.
    """
    valid = valid_mask(means)
    scores = np.full(L_STATES, np.inf)
    for k in range(L_STATES):
        v = valid[k]
        if v.sum() >= min_valid:
            scores[k] = np.sqrt(np.mean((means[k, v] - mu_hat[v]) ** 2))
    if not np.isfinite(scores).any():
        return None
    return int(np.argmin(scores)) + 1


def plurality_vote(beliefs: np.ndarray) -> int:
    """Each participant votes for her highest-probability range (lowest on ties);
    the range with most votes wins (lowest on ties)."""
    votes = np.bincount(np.argmax(beliefs, axis=1), minlength=L_STATES)
    return int(np.argmax(votes)) + 1


def binary_group(state: int) -> int:
    """1 = low (Ranges 1&2), 2 = high (Ranges 3&4)."""
    return 1 if state <= 2 else 2


def group_label(group: int) -> str:
    return "1&2" if group == 1 else "3&4"


def sp_binary_group(mu12: float, alpha12: float) -> int:
    """SP predicts low if mu12 > alpha12, high otherwise (ties go to high)."""
    return 1 if mu12 > alpha12 else 2


# ---------------------------------------------------------------------------
# Small statistics helpers
# ---------------------------------------------------------------------------

def paired_t_p(x, y, alternative: str) -> float:
    """One-sided paired t test p-value (scipy)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if np.allclose(x - y, 0.0):
        return 1.0
    return float(stats.ttest_rel(x, y, alternative=alternative).pvalue)


def paired_t_interval(x, y, level: float = 0.95):
    d = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    n = d.size
    margin = stats.t.ppf(0.5 + level / 2.0, n - 1) * d.std(ddof=1) / np.sqrt(n)
    return float(d.mean() - margin), float(d.mean() + margin)


def classical_first_stage_f(y: np.ndarray, Z: np.ndarray) -> float:
    """Classical F for joint significance of all non-constant columns of Z.

    Z includes a constant; df = (rank(Z) - 1, n - rank(Z)), i.e. (6, n-7) here.
    """
    beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
    ssr = float(np.sum((y - Z @ beta) ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    rank = np.linalg.matrix_rank(Z)
    n = y.size
    return ((tss - ssr) / (rank - 1)) / (ssr / (n - rank))


# ---------------------------------------------------------------------------
# Item-level computations
# ---------------------------------------------------------------------------

def participant_counts(raw_data_path: Path) -> dict:
    """Distinct participants behind the estimation panels and NFTs rated per participant."""
    rows = filter_verified(load_raw_rows(raw_data_path))
    keys_by_nft = defaultdict(set)
    for r in rows:
        keys_by_nft[int(r["NFT"])].add(tuple(r[c] for c in KEY_COLUMNS))
    nfts_per_id = defaultdict(int)
    for keys in keys_by_nft.values():
        for key in keys:
            nfts_per_id[key[0]] += 1
    return {
        "n_keys_by_nft": {k: len(v) for k, v in keys_by_nft.items()},
        "participants": len(nfts_per_id),
        "nfts_per_participant_min": min(nfts_per_id.values()),
        "nfts_per_participant_max": max(nfts_per_id.values()),
    }


def first_stage_diagnostics(panel) -> dict:
    """Retained sample and first-stage F statistics for one NFT (tab:firststage)."""
    Z = np.column_stack([np.ones(panel.n_obs), panel.iv_raw])
    fitted = np.zeros_like(panel.beliefs)
    for j in range(L_STATES):
        beta, *_ = np.linalg.lstsq(Z, panel.beliefs[:, j], rcond=None)
        fitted[:, j] = Z @ beta
    keep = (fitted >= 0.0).all(axis=1)
    f_stats = [classical_first_stage_f(panel.beliefs[:, j], Z) for j in range(3)]
    return {
        "n": panel.n_obs,
        "retained": int(keep.sum()),
        "dropped": int((~keep).sum()),
        "F": f_stats,
    }


def compute_items(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    """Return {nft_id: item dict} with everything needed for the final-paper tables."""
    panels = build_all_panels(raw_data_path, true_state_path)
    items = {}
    for nft_id, p in panels.items():
        mu_hat = p.beliefs.mean(axis=0)
        alpha_hat = p.beliefs_pop.mean(axis=0)

        est = estimate_ols(p, use_iv=True, with_intercept=True)
        means = state_means_from_beta(est.all_beta)
        fs = first_stage_diagnostics(p)
        # estimate_ols drops the same rows for each of the four coordinate regressions.
        assert est.dropped_rows == L_STATES * fs["dropped"]

        pred = {
            "pmba": nearest_state(means, mu_hat),
            "mean_mu": int(np.argmax(mu_hat)) + 1,
            "mean_alpha": int(np.argmax(alpha_hat)) + 1,
            "vote": plurality_vote(p.beliefs),
            "constant_2": 2,
        }
        for d in range(1, L_STATES + 1):
            pred[f"coord_{d}"] = one_coordinate_state(means, mu_hat, d)
        for m in range(1, L_STATES + 1):
            pred[f"own_ge_{m}"] = own_valid_state(means, mu_hat, m)

        robustness = {}
        for method in ROBUSTNESS_METHODS:
            r_means = state_means_from_beta(estimate_by_method(p, method).all_beta)
            robustness[method] = nearest_state(r_means, mu_hat)

        mu12_i = p.beliefs[:, 0] + p.beliefs[:, 1]
        alpha12_i = p.beliefs_pop[:, 0] + p.beliefs_pop[:, 1]
        mu12 = float(mu12_i.mean())
        alpha12 = float(alpha12_i.mean())
        # tab:sp_replication: one-sided one-sample t test of the individual alpha_(1&2)
        # reports against the null mean mu12, in the direction of the observed difference.
        sp_alt = "less" if mu12 > alpha12 else "greater"
        sp_p = float(stats.ttest_1samp(alpha12_i, mu12, alternative=sp_alt).pvalue)

        items[nft_id] = {
            "nft_id": nft_id,
            "true_state": p.true_state,
            "n": p.n_obs,
            "retained": fs["retained"],
            "first_stage_F": fs["F"],
            "mu_hat": mu_hat,
            "alpha_hat": alpha_hat,
            "means": means,
            "pred": pred,
            "robustness": robustness,
            "mu12": mu12,
            "alpha12": alpha12,
            "sp_group": sp_binary_group(mu12, alpha12),
            "sp_p_one_sided": sp_p,
        }
    return items


# ---------------------------------------------------------------------------
# Tables and text numbers
# ---------------------------------------------------------------------------

def abs_errors(items: dict, ids, method: str, source: str = "pred") -> np.ndarray:
    return np.array([abs(items[i][source][method] - items[i]["true_state"]) for i in ids], dtype=float)


def ids_with_truth(items: dict, states) -> list:
    return [i for i in PAPER_NFT_ORDER if items[i]["true_state"] in states]


def accuracy_by_range(items: dict, methods, source: str = "pred") -> dict:
    """MAE and number of exact predictions for each true range and for all items."""
    out = {}
    groups = {str(r): (r,) for r in range(1, 5)}
    groups["all"] = (1, 2, 3, 4)
    for name, states in groups.items():
        ids = ids_with_truth(items, states)
        out[name] = {"items": len(ids)}
        for m in methods:
            err = abs_errors(items, ids, m, source)
            out[name][m] = {"mae": float(err.mean()), "exact": int((err == 0).sum())}
    return out


def prediction_errors_table(items: dict) -> dict:
    """tab:prediction_errors plus the 'Uncertainty' and 'Where does the difference come from' paragraphs."""
    ids = PAPER_NFT_ORDER
    pmba_err = abs_errors(items, ids, "pmba")
    table = {}
    for m in MAIN_METHODS:
        err = abs_errors(items, ids, m)
        row = {"mae": float(err.mean()), "exact": int((err == 0).sum())}
        if m != "pmba":
            row["pmba_minus_method"] = float(pmba_err.mean() - err.mean())
            row["p_paired_t"] = paired_t_p(pmba_err, err, "less")
            row["gain_share_of_benchmark_mae"] = float((err.mean() - pmba_err.mean()) / err.mean())
        table[m] = row

    mu_err = abs_errors(items, ids, "mean_mu")
    alpha_err = abs_errors(items, ids, "mean_alpha")
    diff = pmba_err - mu_err
    gains = [i for i, d in zip(ids, diff) if d < 0]
    losses = [i for i, d in zip(ids, diff) if d > 0]
    raised = [i for i in gains if items[i]["pred"]["mean_mu"] == 1 and items[i]["pred"]["pmba"] > 1]
    lowered = [i for i in gains if items[i]["pred"]["pmba"] < items[i]["pred"]["mean_mu"]
               and items[i]["pred"]["mean_mu"] > items[i]["true_state"]]
    uncertainty = {
        "ci95_vs_mean_mu": paired_t_interval(pmba_err, mu_err),
        "ci95_vs_mean_alpha": paired_t_interval(pmba_err, alpha_err),
        "p_paired_t_vs_mean_mu": paired_t_p(pmba_err, mu_err, "less"),
        "p_signed_rank_vs_mean_mu": wilcoxon_signed_rank_pvalue(pmba_err, mu_err, "less"),
        "improved": len(gains),
        "unchanged": int((diff == 0).sum()),
        "worse": len(losses),
        "improved_items": sorted(gains),
        "raised_above_range1_items": sorted(raised),
        "lowered_overprediction_items": sorted(lowered),
        "worse_items": sorted(losses),
    }
    benchmarks_range4 = ids_with_truth(items, (4,))
    uncertainty["benchmarks_predict_1_for_all_range4"] = all(
        items[i]["pred"][m] == 1 for i in benchmarks_range4 for m in ("mean_mu", "mean_alpha", "vote")
    )
    return {"table": table, "uncertainty": uncertainty}


def constant_benchmark(items: dict) -> dict:
    err = abs_errors(items, PAPER_NFT_ORDER, "constant_2")
    return {"mae": float(err.mean()), "exact": int((err == 0).sum()), "max_error": int(err.max())}


def subgroup_tests_abs_error(items: dict) -> dict:
    """Wilcoxon (exact) and paired t p-values in tab:item_predictions (alternative favours PMBA)."""
    out = {}
    for name, states in SUBSETS.items():
        ids = ids_with_truth(items, states)
        pmba_err = abs_errors(items, ids, "pmba")
        out[name] = {}
        for m in ("mean_mu", "mean_alpha", "vote"):
            err = abs_errors(items, ids, m)
            out[name][m] = {
                "wilcoxon_p": wilcoxon_signed_rank_pvalue(pmba_err, err, "less"),
                "t_p": paired_t_p(pmba_err, err, "less"),
            }
    return out


def score_comparison_table(items: dict) -> dict:
    """tab:score_comparison and the binary SP comparison in Section 4."""
    rows = []
    for i in PAPER_NFT_ORDER:
        it = items[i]
        truth = binary_group(it["true_state"])
        pmba_group = binary_group(it["pred"]["pmba"])
        rows.append({
            "nft_id": i,
            "true_state": it["true_state"],
            "true_group": group_label(truth),
            "pmba_pred": it["pred"]["pmba"],
            "pmba_group": group_label(pmba_group),
            "sp_group": group_label(it["sp_group"]),
            "pmba_score": 1 if pmba_group == truth else -1,
            "sp_score": 1 if it["sp_group"] == truth else -1,
        })
    by_id = {r["nft_id"]: r for r in rows}

    range_avg = {}
    for rng in range(1, 5):
        ids = ids_with_truth(items, (rng,))
        range_avg[str(rng)] = {
            "pmba": float(np.mean([by_id[i]["pmba_score"] for i in ids])),
            "sp": float(np.mean([by_id[i]["sp_score"] for i in ids])),
        }

    tests = {}
    for name, states in SUBSETS.items():
        ids = ids_with_truth(items, states)
        s_pmba = np.array([by_id[i]["pmba_score"] for i in ids], dtype=float)
        s_sp = np.array([by_id[i]["sp_score"] for i in ids], dtype=float)
        tests[name] = {
            "mcnemar_p": mcnemar_exact_pvalue((s_pmba == 1).astype(int), (s_sp == 1).astype(int)),
            "wilcoxon_p": wilcoxon_signed_rank_pvalue(s_pmba, s_sp, "greater"),
            "t_p": paired_t_p(s_pmba, s_sp, "greater"),
        }

    return {
        "rows": rows,
        "range_avg": range_avg,
        "total_pmba": int(sum(r["pmba_score"] for r in rows)),
        "total_sp": int(sum(r["sp_score"] for r in rows)),
        "correct_pmba": int(sum(r["pmba_score"] == 1 for r in rows)),
        "correct_sp": int(sum(r["sp_score"] == 1 for r in rows)),
        "tests": tests,
    }


def validity_summary(items: dict) -> dict:
    """Component-bound and adding-up checks on the 80 estimated state-contingent vectors."""
    all_means = np.stack([items[i]["means"] for i in PAPER_NFT_ORDER])  # (20, 4 states, 4 coords)
    comps = all_means.ravel()
    sums = all_means.sum(axis=2).ravel()
    selected_oob = 0
    for i in PAPER_NFT_ORDER:
        k = items[i]["pred"]["pmba"]
        if not valid_mask(items[i]["means"][k - 1]).all():
            selected_oob += 1
    return {
        "n_components": int(comps.size),
        "n_negative": int((comps < 0).sum()),
        "n_above_one": int((comps > 1).sum()),
        "n_within": int(((comps >= 0) & (comps <= 1)).sum()),
        "share_within_pct": float(100.0 * ((comps >= 0) & (comps <= 1)).mean()),
        "share_negative_pct": float(100.0 * (comps < 0).mean()),
        "share_above_pct": float(100.0 * (comps > 1).mean()),
        "n_vectors": int(sums.size),
        "max_abs_sum_error": float(np.max(np.abs(sums - 1.0))),
        "sum_errors": (sums - 1.0).tolist(),
        "selected_out_of_bounds": selected_oob,
        "components": comps.tolist(),
    }


def component_histogram(components, width: float = 0.2) -> dict:
    """Histogram used for panel (a) of State_contingent_Vec_dist.png: bins of
    width 0.2 aligned at 0 and 1, i.e. [a, a+0.2).  Returns {left edge: count}."""
    comps = np.asarray(components, dtype=float)
    lefts = np.floor(np.round(comps / width, 9)).astype(int)
    counts = defaultdict(int)
    for left in lefts:
        counts[round(left * width, 1)] += 1
    return dict(sorted(counts.items()))


def validity_grid(items: dict) -> list:
    """Rows of valid_grid.png: for each NFT (paper order), 16 cells (candidate state
    1..4 x coordinate 1..4) coded 'N' (< 0), 'V' (in [0,1]) or 'A' (> 1)."""
    rows = []
    for i in PAPER_NFT_ORDER:
        m = items[i]["means"]
        cells = []
        for k in range(L_STATES):
            for d in range(L_STATES):
                x = m[k, d]
                cells.append("N" if x < 0 else ("A" if x > 1 else "V"))
        rows.append({"nft_id": i, "true_state": items[i]["true_state"], "cells": "".join(cells)})
    return rows


def alternative_matching_table(items: dict) -> dict:
    acc = accuracy_by_range(items, ALT_METHODS)
    own_ge_4_missing = [i for i in PAPER_NFT_ORDER if items[i]["pred"]["own_ge_4"] is None]
    all_acc = acc["all"]
    benchmarks = ("mean_mu", "mean_alpha", "vote")
    specs = ("pmba", "coord_1", "coord_2", "coord_3", "coord_4", "own_ge_1", "own_ge_2", "own_ge_3")
    text = {
        "pmba_specs_beat_all_benchmarks_on_mae": all(
            all_acc[s]["mae"] < all_acc[b]["mae"] for s in specs for b in benchmarks
        ),
        "valid_coordinate_exact_min": min(all_acc[s]["exact"] for s in ("own_ge_1", "own_ge_2", "own_ge_3")),
        "valid_coordinate_exact_max": max(all_acc[s]["exact"] for s in ("own_ge_1", "own_ge_2", "own_ge_3")),
        "baseline_and_benchmarks_exact_max": max(all_acc[s]["exact"] for s in ("pmba",) + benchmarks),
        "own_ge_4_nfts_without_candidate": own_ge_4_missing,
    }
    return {"accuracy": acc, "text": text}


def robustness_table(items: dict) -> dict:
    """tab:rob1: predictions, MAE by range, one-sided paired t vs mean first-order belief rule."""
    by_range = {}
    for rng in range(1, 5):
        ids = ids_with_truth(items, (rng,))
        by_range[str(rng)] = {m: float(abs_errors(items, ids, m, "robustness").mean()) for m in ROBUSTNESS_METHODS}
        by_range[str(rng)]["mean_mu"] = float(abs_errors(items, ids, "mean_mu").mean())
    mu_err = abs_errors(items, PAPER_NFT_ORDER, "mean_mu")
    p_values = {
        m: paired_t_p(abs_errors(items, PAPER_NFT_ORDER, m, "robustness"), mu_err, "less")
        for m in ROBUSTNESS_METHODS
    }
    return {"mae_by_range": by_range, "p_paired_t": p_values}


def first_stage_summary(items: dict) -> dict:
    f_all = [f for i in PAPER_NFT_ORDER for f in items[i]["first_stage_F"]]
    return {
        "F_min": float(min(f_all)),
        "F_max": float(max(f_all)),
        "F_count": len(f_all),
        "F_below_10": int(sum(f < 10 for f in f_all)),
        "dropped_pairs": int(sum(items[i]["n"] - items[i]["retained"] for i in PAPER_NFT_ORDER)),
        "n_min": int(min(items[i]["n"] for i in PAPER_NFT_ORDER)),
        "n_max": int(max(items[i]["n"] for i in PAPER_NFT_ORDER)),
    }


def compute_all(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    items = compute_items(raw_data_path, true_state_path)
    validity = validity_summary(items)
    return {
        "items": items,
        "sample": participant_counts(raw_data_path),
        "first_stage": first_stage_summary(items),
        "prediction_errors": prediction_errors_table(items),
        "true_range": accuracy_by_range(items, MAIN_METHODS),
        "constant_2": constant_benchmark(items),
        "subgroup_tests": subgroup_tests_abs_error(items),
        "score_comparison": score_comparison_table(items),
        "validity": validity,
        "histogram": component_histogram(validity["components"]),
        "validity_grid": validity_grid(items),
        "alternative_matching": alternative_matching_table(items),
        "robustness": robustness_table(items),
    }


# ---------------------------------------------------------------------------
# Flatten results into checkable values keyed like the expectations module
# ---------------------------------------------------------------------------

def flat_values(res: dict) -> dict:
    """Map every checkable quantity to a key of the form '<paper label>/<field>'."""
    items = res["items"]
    v = {}

    # Section 4.1-4.2: sample and first stage
    s = res["sample"]
    v["sec4:sample/participants"] = s["participants"]
    v["sec4:sample/nfts_per_participant_min"] = s["nfts_per_participant_min"]
    v["sec4:sample/nfts_per_participant_max"] = s["nfts_per_participant_max"]
    fs = res["first_stage"]
    v["sec4:implementation/n_min"] = fs["n_min"]
    v["sec4:implementation/n_max"] = fs["n_max"]
    v["sec4:implementation/dropped_pairs"] = fs["dropped_pairs"]
    v["sec4:implementation/F_min"] = fs["F_min"]
    v["sec4:implementation/F_max"] = fs["F_max"]
    v["tab:firststage/F_count"] = fs["F_count"]
    v["tab:firststage/F_below_10"] = fs["F_below_10"]
    for i in PAPER_NFT_ORDER:
        it = items[i]
        v[f"tab:firststage/nft{i}/n"] = it["n"]
        v[f"tab:firststage/nft{i}/retained"] = it["retained"]
        for d in range(3):
            v[f"tab:firststage/nft{i}/F_range{d + 1}"] = it["first_stage_F"][d]

    # tab:prediction_errors and surrounding text
    pe = res["prediction_errors"]
    for m, row in pe["table"].items():
        for field, val in row.items():
            v[f"tab:prediction_errors/{m}/{field}"] = val
    gains = [pe["table"][m]["pmba_minus_method"] for m in ("mean_mu", "mean_alpha", "vote")]
    shares = [100 * pe["table"][m]["gain_share_of_benchmark_mae"] for m in ("mean_mu", "mean_alpha", "vote")]
    v["sec4:results/gain_min"] = -max(gains)
    v["sec4:results/gain_max"] = -min(gains)
    v["sec4:results/gain_share_min_pct"] = min(shares)
    v["sec4:results/gain_share_max_pct"] = max(shares)
    u = pe["uncertainty"]
    v["sec4:uncertainty/ci95_vs_mean_mu_lo"] = u["ci95_vs_mean_mu"][0]
    v["sec4:uncertainty/ci95_vs_mean_mu_hi"] = u["ci95_vs_mean_mu"][1]
    v["sec4:uncertainty/ci95_vs_mean_alpha_lo"] = u["ci95_vs_mean_alpha"][0]
    v["sec4:uncertainty/ci95_vs_mean_alpha_hi"] = u["ci95_vs_mean_alpha"][1]
    v["sec4:uncertainty/p_paired_t_vs_mean_mu"] = u["p_paired_t_vs_mean_mu"]
    v["sec4:uncertainty/p_signed_rank_vs_mean_mu"] = u["p_signed_rank_vs_mean_mu"]
    for key in ("improved", "unchanged", "worse"):
        v[f"sec4:where/{key}"] = u[key]
    for key in ("improved_items", "raised_above_range1_items", "lowered_overprediction_items", "worse_items"):
        v[f"sec4:where/{key}"] = ",".join(str(x) for x in u[key])
    v["sec4:discussion/benchmarks_predict_1_for_all_range4"] = u["benchmarks_predict_1_for_all_range4"]

    # tab:true_range (identical numbers also appear in tab:item_predictions)
    for label in ("tab:true_range", "tab:item_predictions"):
        for rng, row in res["true_range"].items():
            v[f"{label}/range{rng}/items"] = row["items"]
            for m in MAIN_METHODS:
                v[f"{label}/range{rng}/{m}/mae"] = row[m]["mae"]
                v[f"{label}/range{rng}/{m}/exact"] = row[m]["exact"]

    c2 = res["constant_2"]
    v["sec4:constant_range2/mae"] = c2["mae"]
    v["sec4:constant_range2/exact"] = c2["exact"]
    v["sec4:constant_range2/max_error"] = c2["max_error"]

    # tab:item_predictions rows and subgroup tests
    for i in PAPER_NFT_ORDER:
        for m in MAIN_METHODS:
            v[f"tab:item_predictions/nft{i}/{m}"] = items[i]["pred"][m]
            v[f"tab:item_predictions/nft{i}/{m}_abs_error"] = abs(items[i]["pred"][m] - items[i]["true_state"])
    for subset, by_m in res["subgroup_tests"].items():
        for m, tests in by_m.items():
            v[f"tab:item_predictions/{subset}/{m}/wilcoxon_p"] = tests["wilcoxon_p"]
            v[f"tab:item_predictions/{subset}/{m}/t_p"] = tests["t_p"]

    # Binary SP comparison and tab:score_comparison
    sc = res["score_comparison"]
    v["sec4:sp/pmba_correct"] = sc["correct_pmba"]
    v["sec4:sp/sp_correct"] = sc["correct_sp"]
    v["sec4:sp/mcnemar_p"] = sc["tests"]["all"]["mcnemar_p"]
    for r in sc["rows"]:
        i = r["nft_id"]
        for field in ("true_group", "pmba_pred", "pmba_group", "sp_group", "pmba_score", "sp_score"):
            v[f"tab:score_comparison/nft{i}/{field}"] = r[field]
    for rng, avg in sc["range_avg"].items():
        v[f"tab:score_comparison/range{rng}/avg_pmba"] = avg["pmba"]
        v[f"tab:score_comparison/range{rng}/avg_sp"] = avg["sp"]
    v["tab:score_comparison/total_pmba"] = sc["total_pmba"]
    v["tab:score_comparison/total_sp"] = sc["total_sp"]
    for subset, tests in sc["tests"].items():
        for name, p in tests.items():
            v[f"tab:score_comparison/{subset}/{name}"] = p

    # Validity paragraph and the two figures
    va = res["validity"]
    for key in ("n_components", "n_negative", "n_above_one", "n_within", "share_within_pct", "selected_out_of_bounds"):
        v[f"sec4:validity/{key}"] = va[key]
    v["fig:state_mean_distribution/n_vectors"] = va["n_vectors"]
    v["fig:state_mean_distribution/all_sums_one"] = va["max_abs_sum_error"] < 1e-12
    v["fig:state_mean_distribution/n_negative"] = va["n_negative"]
    v["fig:state_mean_distribution/n_within"] = va["n_within"]
    v["fig:state_mean_distribution/n_above_one"] = va["n_above_one"]
    v["fig:state_mean_distribution/share_negative_pct"] = va["share_negative_pct"]
    v["fig:state_mean_distribution/share_within_pct"] = va["share_within_pct"]
    v["fig:state_mean_distribution/share_above_pct"] = va["share_above_pct"]
    for left, count in res["histogram"].items():
        v[f"fig:state_mean_distribution/bin_{left:+.1f}"] = count
    for row in res["validity_grid"]:
        v[f"fig:validity/nft{row['nft_id']}"] = row["cells"]

    # Alternative-matching table
    for i in PAPER_NFT_ORDER:
        for m in ALT_METHODS:
            v[f"alternative-matching/nft{i}/{m}"] = items[i]["pred"][m]
    for rng, row in res["alternative_matching"]["accuracy"].items():
        for m in ALT_METHODS:
            v[f"alternative-matching/state{rng}/{m}/exact"] = row[m]["exact"]
            v[f"alternative-matching/state{rng}/{m}/mae"] = row[m]["mae"]
    t = res["alternative_matching"]["text"]
    v["sec4:validity/pmba_specs_beat_all_benchmarks_on_mae"] = t["pmba_specs_beat_all_benchmarks_on_mae"]
    v["sec4:validity/valid_coordinate_exact_min"] = t["valid_coordinate_exact_min"]
    v["sec4:validity/valid_coordinate_exact_max"] = t["valid_coordinate_exact_max"]
    v["sec4:validity/baseline_and_benchmarks_exact_max"] = t["baseline_and_benchmarks_exact_max"]
    acc_all = res["alternative_matching"]["accuracy"]["all"]
    v["sec4:validity/coord_1_exact"] = acc_all["coord_1"]["exact"]
    v["sec4:validity/coord_4_exact"] = acc_all["coord_4"]["exact"]
    v["sec4:validity/mean_alpha_exact"] = acc_all["mean_alpha"]["exact"]
    v["alternative-matching/own_ge_4_has_nft_without_candidate"] = len(t["own_ge_4_nfts_without_candidate"]) > 0

    # tab:rob1
    for i in PAPER_NFT_ORDER:
        for m in ROBUSTNESS_METHODS:
            v[f"tab:rob1/nft{i}/{m}"] = items[i]["robustness"][m]
        v[f"tab:rob1/nft{i}/mean_mu"] = items[i]["pred"]["mean_mu"]
    for rng, row in res["robustness"]["mae_by_range"].items():
        for m, val in row.items():
            v[f"tab:rob1/range{rng}/{m}/mae"] = val
    for m, p in res["robustness"]["p_paired_t"].items():
        v[f"tab:rob1/p_paired_t/{m}"] = p
    v["tab:rob1/ols_iv_c_equals_ols_iv_nc"] = all(
        items[i]["robustness"]["ols_iv_c"] == items[i]["robustness"]["ols_iv_nc"] for i in PAPER_NFT_ORDER
    )

    # tab:nft_list: assigned range equals the true state used in the analysis
    for i in PAPER_NFT_ORDER:
        v[f"tab:nft_list/nft{i}/range"] = items[i]["true_state"]

    # tab:sp_replication
    for i in PAPER_NFT_ORDER:
        it = items[i]
        v[f"tab:sp_replication/nft{i}/n"] = it["n"]
        v[f"tab:sp_replication/nft{i}/mu12_pct"] = 100.0 * it["mu12"]
        v[f"tab:sp_replication/nft{i}/alpha12_pct"] = 100.0 * it["alpha12"]
        v[f"tab:sp_replication/nft{i}/sp_group"] = group_label(it["sp_group"])
        v[f"tab:sp_replication/nft{i}/p_one_sided"] = it["sp_p_one_sided"]

    return v
