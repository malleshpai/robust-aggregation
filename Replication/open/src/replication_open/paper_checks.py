from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .paper_expectations import (
    PAPER_NFT_ORDER,
    PREDICTION_ERRORS_EXPECTED,
    PREDICTION_ERRORS_SUMMARY_EXPECTED,
    ROBUSTNESS_EXPECTED,
    ROBUSTNESS_SUMMARY_EXPECTED,
    SCORE_COMPARISON_SUMMARY_EXPECTED,
    SP_REPLICATION_EXPECTED,
)
from .paper_tables import write_paper_tables


def _isclose(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def run_crosscheck(out_dir: Path) -> dict:
    computed = write_paper_tables(out_dir)

    mismatches: List[dict] = []
    matches: List[dict] = []

    # 1) Prediction accuracy table rows
    pred_rows = {r["nft_id"]: r for r in computed["prediction_accuracy"]["rows"]}
    for nft in PAPER_NFT_ORDER:
        got = pred_rows[nft]
        exp = PREDICTION_ERRORS_EXPECTED[nft]
        for col, got_col in [("pmba", "pmba_pred"), ("majority_mu", "majority_mu_pred"), ("majority_alpha", "majority_alpha_pred")]:
            if got[got_col] == exp[col]:
                matches.append({"section": "prediction_rows", "nft_id": nft, "field": col})
            else:
                mismatches.append({"section": "prediction_rows", "nft_id": nft, "field": col, "expected": exp[col], "got": got[got_col]})

    # 2) Prediction summary stats
    pred_sum = computed["prediction_accuracy"]["summary"]
    for k, exp in PREDICTION_ERRORS_SUMMARY_EXPECTED.items():
        got = pred_sum[k]
        tol = 1e-4
        if _isclose(got, exp, tol):
            matches.append({"section": "prediction_summary", "field": k})
        else:
            mismatches.append({"section": "prediction_summary", "field": k, "expected": exp, "got": got})

    # 3) Robustness row predictions
    rob_rows = {r["nft_id"]: r for r in computed["robustness"]["rows"]}
    for nft in PAPER_NFT_ORDER:
        got = rob_rows[nft]
        exp = ROBUSTNESS_EXPECTED[nft]
        for col in ["ols_iv_c", "cls_iv_c", "ols_iv_nc", "cls_iv_nc", "ols_noiv_c", "cls_noiv_c", "majority"]:
            got_col = col if col != "majority" else "majority"
            if got[got_col] == exp[col]:
                matches.append({"section": "robustness_rows", "nft_id": nft, "field": col})
            else:
                mismatches.append({"section": "robustness_rows", "nft_id": nft, "field": col, "expected": exp[col], "got": got[got_col]})

    # 4) Robustness summary
    rob_sum = computed["robustness"]["summary"]
    for rng in ["range_1", "range_2", "range_3", "range_4"]:
        for col, exp in ROBUSTNESS_SUMMARY_EXPECTED[rng].items():
            got = rob_sum[rng][col]
            tol = 0.011  # paper displays rounded values (e.g., 0.86, 1.14)
            if _isclose(got, exp, tol):
                matches.append({"section": "robustness_summary", "field": f"{rng}.{col}"})
            else:
                mismatches.append({"section": "robustness_summary", "field": f"{rng}.{col}", "expected": exp, "got": got})

    for col, exp in ROBUSTNESS_SUMMARY_EXPECTED["paired_t_p"].items():
        got = rob_sum["paired_t_p"][col]
        if _isclose(got, exp, 1e-4):
            matches.append({"section": "robustness_summary", "field": f"paired_t_p.{col}"})
        else:
            mismatches.append({"section": "robustness_summary", "field": f"paired_t_p.{col}", "expected": exp, "got": got})

    # 5) SP replication row checks
    sp_rows = {r["nft_id"]: r for r in computed["sp_replication"]["rows"]}
    for nft in PAPER_NFT_ORDER:
        got = sp_rows[nft]
        exp = SP_REPLICATION_EXPECTED[nft]

        checks = [
            ("n_obs", got["n_obs"], exp["n_obs"], 0.0),
            ("mu12_pct", got["mu12_pct"], exp["mu12_pct"], 0.01),
            ("alpha12_pct", got["alpha12_pct"], exp["alpha12_pct"], 0.01),
            ("sp_group", got["sp_group"], exp["sp_group"], None),
            ("p_value", got["p_value_one_sided"], exp["p_value"], 0.03),
        ]

        for field, got_v, exp_v, tol in checks:
            ok = (got_v == exp_v) if tol is None else _isclose(float(got_v), float(exp_v), tol)
            if ok:
                matches.append({"section": "sp_replication", "nft_id": nft, "field": field})
            else:
                mismatches.append({"section": "sp_replication", "nft_id": nft, "field": field, "expected": exp_v, "got": got_v})

    # 6) Score comparison summary checks
    score_sum = computed["score_comparison"]["summary"]
    for k, exp in SCORE_COMPARISON_SUMMARY_EXPECTED.items():
        got = score_sum[k]
        tol = 0.011 if k.startswith("range_") and "avg" in k else 1e-4
        if _isclose(float(got), float(exp), tol):
            matches.append({"section": "score_summary", "field": k})
        else:
            mismatches.append({"section": "score_summary", "field": k, "expected": exp, "got": got})

    report = {
        "n_matches": len(matches),
        "n_mismatches": len(mismatches),
        "matches": matches,
        "mismatches": mismatches,
    }

    (out_dir / "paper_crosscheck_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_markdown_report(out_dir / "paper_crosscheck_report.md", report)

    return report


def _write_markdown_report(path: Path, report: dict) -> None:
    lines = []
    lines.append("# Cross-check against the original submission's tables")
    lines.append("")
    lines.append(f"- Total matches: **{report['n_matches']}**")
    lines.append(f"- Total mismatches: **{report['n_mismatches']}**")
    lines.append("")

    if report["mismatches"]:
        lines.append("## Mismatches")
        lines.append("")
        lines.append("| Section | NFT | Field | Expected | Got |")
        lines.append("|---|---:|---|---:|---:|")
        for m in report["mismatches"]:
            nft = m.get("nft_id", "")
            lines.append(f"| {m['section']} | {nft} | {m['field']} | {m['expected']} | {m['got']} |")
        lines.append("")
    else:
        lines.append("## Mismatches")
        lines.append("")
        lines.append("None.")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This report compares computed open-source outputs against values hard-coded from the tables of the original submission (`paper_expectations.py`).")
    lines.append("- The final paper (`../../paper/main.tex`) is checked separately by `make check-final` (`outputs/final_paper/final_paper_check.md`).")
    lines.append("- Differences can reflect (i) paper typos/internal inconsistencies, or (ii) numerical differences in nonlinear CLS optimization relative to Stata `nl`.")
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
