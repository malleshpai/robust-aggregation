from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np

from .config import DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE
from .data_prep import build_all_panels
from .paper_expectations import PAPER_NFT_ORDER
from .pipeline import DEFAULT_METHODS, run_replication
from .stats import (
    mcnemar_exact_pvalue,
    one_sample_t_pvalue,
    paired_t_test_pvalue,
    wilcoxon_signed_rank_pvalue,
)


def _order_rows(rows: List[dict], key: str = "nft_id") -> List[dict]:
    by_id = {r[key]: r for r in rows}
    return [by_id[n] for n in PAPER_NFT_ORDER]


def _write_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _group_label(state: int) -> str:
    return "1&2" if state in (1, 2) else "3&4"


@lru_cache(maxsize=4)
def _paper_context_cached(raw_data_path_str: str, true_state_path_str: str):
    raw_data_path = Path(raw_data_path_str)
    true_state_path = Path(true_state_path_str)
    panels = build_all_panels(raw_data_path, true_state_path)
    run = run_replication(raw_data_path, true_state_path, methods=DEFAULT_METHODS)
    pred_rows = {r["nft_id"]: r for r in run["prediction_rows"]}
    return panels, pred_rows


def _paper_context(raw_data_path: Path, true_state_path: Path):
    return _paper_context_cached(str(raw_data_path.resolve()), str(true_state_path.resolve()))


def build_prediction_errors_table(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    panels, pred_rows = _paper_context(raw_data_path, true_state_path)

    rows: List[dict] = []
    for nft_id in PAPER_NFT_ORDER:
        p = panels[nft_id]
        mu_hat = p.beliefs.mean(axis=0)
        alpha_hat = p.beliefs_pop.mean(axis=0)

        pmba_pred = pred_rows[nft_id]["ols_iv_c_pred"]
        majority_mu = int(np.argmax(mu_hat)) + 1
        majority_alpha = int(np.argmax(alpha_hat)) + 1

        rows.append(
            {
                "nft_id": nft_id,
                "true_state": p.true_state,
                "pmba_pred": pmba_pred,
                "majority_mu_pred": majority_mu,
                "majority_alpha_pred": majority_alpha,
                "pmba_abs_error": abs(pmba_pred - p.true_state),
                "majority_mu_abs_error": abs(majority_mu - p.true_state),
                "majority_alpha_abs_error": abs(majority_alpha - p.true_state),
            }
        )

    pmba_err = np.array([r["pmba_abs_error"] for r in rows], dtype=float)
    mu_err = np.array([r["majority_mu_abs_error"] for r in rows], dtype=float)
    alpha_err = np.array([r["majority_alpha_abs_error"] for r in rows], dtype=float)

    summary = {
        "mae_pmba": float(np.mean(pmba_err)),
        "mae_majority_mu": float(np.mean(mu_err)),
        "mae_majority_alpha": float(np.mean(alpha_err)),
        "wilcoxon_p_vs_majority_mu": float(wilcoxon_signed_rank_pvalue(pmba_err, mu_err, alternative="less")),
        "wilcoxon_p_vs_majority_alpha": float(wilcoxon_signed_rank_pvalue(pmba_err, alpha_err, alternative="less")),
        "ttest_p_vs_majority_mu": float(paired_t_test_pvalue(pmba_err, mu_err, alternative="less")),
        "ttest_p_vs_majority_alpha": float(paired_t_test_pvalue(pmba_err, alpha_err, alternative="less")),
    }

    return {"rows": rows, "summary": summary}


def build_score_comparison_table(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    panels, pred_rows = _paper_context(raw_data_path, true_state_path)

    rows: List[dict] = []
    for nft_id in PAPER_NFT_ORDER:
        p = panels[nft_id]
        pmba_pred = pred_rows[nft_id]["ols_iv_c_pred"]
        sp_group = pred_rows[nft_id]["sp_group"]

        true_group = _group_label(p.true_state)
        pmba_group = _group_label(pmba_pred)

        pmba_score = 1 if pmba_group == true_group else -1
        sp_score = 1 if sp_group == true_group else -1

        rows.append(
            {
                "nft_id": nft_id,
                "true_state": p.true_state,
                "true_group": true_group,
                "pmba_pred": pmba_pred,
                "pmba_group": pmba_group,
                "sp_group": sp_group,
                "pmba_score": pmba_score,
                "sp_score": sp_score,
            }
        )

    arr_pmba = np.array([r["pmba_score"] for r in rows], dtype=float)
    arr_sp = np.array([r["sp_score"] for r in rows], dtype=float)

    range_avgs = {}
    for rng in (1, 2, 3, 4):
        idx = [i for i, r in enumerate(rows) if r["true_state"] == rng]
        range_avgs[f"range_{rng}_avg_pmba"] = float(np.mean(arr_pmba[idx]))
        range_avgs[f"range_{rng}_avg_sp"] = float(np.mean(arr_sp[idx]))

    subsets = {
        "range12": [i for i, r in enumerate(rows) if r["true_state"] in (1, 2)],
        "range123": [i for i, r in enumerate(rows) if r["true_state"] in (1, 2, 3)],
        "all": list(range(len(rows))),
    }

    test_summary = {}
    for name, idx in subsets.items():
        s1 = arr_pmba[idx]
        s2 = arr_sp[idx]
        success1 = (s1 == 1).astype(int)
        success2 = (s2 == 1).astype(int)
        test_summary[f"{name}_mcnemar_p"] = float(mcnemar_exact_pvalue(success1, success2))
        test_summary[f"{name}_wilcoxon_p"] = float(wilcoxon_signed_rank_pvalue(s1, s2, alternative="greater"))
        test_summary[f"{name}_ttest_p"] = float(paired_t_test_pvalue(s1, s2, alternative="greater"))

    summary = {
        **range_avgs,
        "total_score_pmba": int(np.sum(arr_pmba)),
        "total_score_sp": int(np.sum(arr_sp)),
        **test_summary,
    }

    return {"rows": rows, "summary": summary}


def build_robustness_table(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    panels, pred_rows = _paper_context(raw_data_path, true_state_path)

    method_cols = ["ols_iv_c", "cls_iv_c", "ols_iv_nc", "cls_iv_nc", "ols_noiv_c", "cls_noiv_c"]

    rows: List[dict] = []
    for nft_id in PAPER_NFT_ORDER:
        p = panels[nft_id]
        row = {
            "nft_id": nft_id,
            "true_state": p.true_state,
            "majority": pred_rows[nft_id]["majority_pred"],
        }
        for m in method_cols:
            row[m] = pred_rows[nft_id][f"{m}_pred"]
            row[f"{m}_abs_error"] = abs(row[m] - p.true_state)
        row["majority_abs_error"] = abs(row["majority"] - p.true_state)
        rows.append(row)

    summary = {}
    for rng in (1, 2, 3, 4):
        rr = [r for r in rows if r["true_state"] == rng]
        summary[f"range_{rng}"] = {
            m: float(np.mean([r[f"{m}_abs_error"] for r in rr])) for m in method_cols
        }
        summary[f"range_{rng}"]["majority"] = float(np.mean([r["majority_abs_error"] for r in rr]))

    majority_err = np.array([r["majority_abs_error"] for r in rows], dtype=float)
    summary["paired_t_p"] = {
        m: float(paired_t_test_pvalue(np.array([r[f"{m}_abs_error"] for r in rows], dtype=float), majority_err, alternative="less"))
        for m in method_cols
    }

    return {"rows": rows, "summary": summary}


def build_sp_replication_table(raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    panels, pred_rows = _paper_context(raw_data_path, true_state_path)

    rows: List[dict] = []
    for nft_id in PAPER_NFT_ORDER:
        p = panels[nft_id]
        mu12 = p.beliefs[:, 0] + p.beliefs[:, 1]
        alpha12 = p.beliefs_pop[:, 0] + p.beliefs_pop[:, 1]

        mu12_mean = float(np.mean(mu12))
        alpha12_mean = float(np.mean(alpha12))
        alt = "greater" if mu12_mean > alpha12_mean else "less"
        # Match manuscript computation: one-sample test of mu12 around mean(alpha12).
        pval = one_sample_t_pvalue(mu12, alpha12_mean, alternative=alt)

        rows.append(
            {
                "nft_id": nft_id,
                "true_state": p.true_state,
                "n_obs": p.n_obs,
                "mu12_pct": 100.0 * mu12_mean,
                "alpha12_pct": 100.0 * alpha12_mean,
                "sp_group": pred_rows[nft_id]["sp_group"],
                "p_value_one_sided": float(pval),
            }
        )

    return {"rows": rows, "summary": {"n_nfts": len(rows)}}


def write_paper_tables(out_dir: Path, raw_data_path: Path = DEFAULT_RAW_DATA, true_state_path: Path = DEFAULT_TRUE_STATE) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    latex_dir = out_dir / "latex"
    latex_dir.mkdir(parents=True, exist_ok=True)

    pred = build_prediction_errors_table(raw_data_path, true_state_path)
    score = build_score_comparison_table(raw_data_path, true_state_path)
    rob = build_robustness_table(raw_data_path, true_state_path)
    sp = build_sp_replication_table(raw_data_path, true_state_path)

    _write_csv(out_dir / "table_prediction_accuracy.csv", pred["rows"])
    _write_csv(out_dir / "table_score_comparison.csv", score["rows"])
    _write_csv(out_dir / "table_robustness_predictions.csv", rob["rows"])
    _write_csv(out_dir / "table_sp_replication.csv", sp["rows"])

    (out_dir / "table_prediction_accuracy_summary.json").write_text(json.dumps(pred["summary"], indent=2), encoding="utf-8")
    (out_dir / "table_score_comparison_summary.json").write_text(json.dumps(score["summary"], indent=2), encoding="utf-8")
    (out_dir / "table_robustness_summary.json").write_text(json.dumps(rob["summary"], indent=2), encoding="utf-8")

    # Lightweight LaTeX fragments (data body only) for easier manuscript syncing.
    (latex_dir / "prediction_accuracy_rows.tex").write_text(
        "\n".join(
            f"{r['nft_id']} & {r['true_state']} & {r['pmba_pred']} & {r['majority_mu_pred']} & {r['majority_alpha_pred']} & {r['pmba_abs_error']} & {r['majority_mu_abs_error']} & {r['majority_alpha_abs_error']} \\\\"
            for r in pred["rows"]
        )
        + "\n",
        encoding="utf-8",
    )

    (latex_dir / "robustness_rows.tex").write_text(
        "\n".join(
            f"{r['nft_id']} & {r['true_state']} & {r['ols_iv_c']} & {r['cls_iv_c']} & {r['ols_iv_nc']} & {r['cls_iv_nc']} & {r['ols_noiv_c']} & {r['cls_noiv_c']} & {r['majority']} \\\\"
            for r in rob["rows"]
        )
        + "\n",
        encoding="utf-8",
    )

    (latex_dir / "sp_replication_rows.tex").write_text(
        "\n".join(
            f"{r['nft_id']} & {r['true_state']} & {r['mu12_pct']:.2f}\\% & {r['alpha12_pct']:.2f}\\% & {r['sp_group']} & ({r['p_value_one_sided']:.4f}) \\\\"
            for r in sp["rows"]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "prediction_accuracy": pred,
        "score_comparison": score,
        "robustness": rob,
        "sp_replication": sp,
    }
