"""Write the final-paper results (CSV/JSON) and redraw the two appendix figures."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .final_paper import (
    ALT_METHODS,
    MAIN_METHODS,
    PAPER_NFT_ORDER,
    ROBUSTNESS_METHODS,
    compute_all,
    flat_values,
    group_label,
)


def _write_csv(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_to_builtin) + "\n", encoding="utf-8")


def _to_builtin(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    raise TypeError(f"Cannot serialise {type(x)}")


def _component_class(x: float) -> str:
    return "below_0" if x < 0 else ("above_1" if x > 1 else "within_0_1")


def write_tables(res: dict, out_dir: Path) -> None:
    items = res["items"]

    # Item level: everything per NFT in one file.
    rows = []
    for i in PAPER_NFT_ORDER:
        it = items[i]
        row = {"nft_id": i, "true_state": it["true_state"], "n": it["n"], "retained": it["retained"]}
        for d in range(3):
            row[f"first_stage_F_range{d + 1}"] = it["first_stage_F"][d]
        for m in ALT_METHODS + ["own_ge_4", "constant_2"]:
            row[m] = it["pred"][m]
        for m in ROBUSTNESS_METHODS:
            row[f"rob_{m}"] = it["robustness"][m]
        row["mu12"] = it["mu12"]
        row["alpha12"] = it["alpha12"]
        row["sp_group"] = group_label(it["sp_group"])
        row["sp_p_one_sided"] = it["sp_p_one_sided"]
        rows.append(row)
    _write_csv(out_dir / "item_level.csv", rows)

    # tab:prediction_errors
    pe = res["prediction_errors"]["table"]
    _write_csv(out_dir / "table_prediction_errors.csv", [
        {"method": m, "mae": pe[m]["mae"], "exact": pe[m]["exact"],
         "pmba_minus_method": pe[m].get("pmba_minus_method", ""), "p_paired_t": pe[m].get("p_paired_t", "")}
        for m in MAIN_METHODS
    ])

    # tab:true_range (also the summary rows of tab:item_predictions)
    tr_rows = []
    for rng, row in res["true_range"].items():
        out = {"true_range": rng, "items": row["items"]}
        for m in MAIN_METHODS:
            out[f"{m}_mae"] = row[m]["mae"]
            out[f"{m}_exact"] = row[m]["exact"]
        tr_rows.append(out)
    _write_csv(out_dir / "table_true_range.csv", tr_rows)

    # tab:item_predictions rows and subgroup tests
    ip_rows = []
    for i in PAPER_NFT_ORDER:
        it = items[i]
        out = {"nft_id": i, "true_state": it["true_state"]}
        for m in MAIN_METHODS:
            out[m] = it["pred"][m]
        for m in MAIN_METHODS:
            out[f"{m}_abs_error"] = abs(it["pred"][m] - it["true_state"])
        ip_rows.append(out)
    _write_csv(out_dir / "table_item_predictions.csv", ip_rows)
    _write_csv(out_dir / "table_item_predictions_tests.csv", [
        {"subset": s, "benchmark": m, "wilcoxon_p": t["wilcoxon_p"], "t_p": t["t_p"]}
        for s, by_m in res["subgroup_tests"].items() for m, t in by_m.items()
    ])

    # tab:score_comparison
    sc = res["score_comparison"]
    _write_csv(out_dir / "table_score_comparison.csv", sc["rows"])
    _write_csv(out_dir / "table_score_comparison_tests.csv", [
        {"subset": s, **t} for s, t in sc["tests"].items()
    ])

    # Alternative-matching table
    _write_csv(out_dir / "table_alternative_matching.csv", [
        {"nft_id": i, "true_state": items[i]["true_state"], **{m: items[i]["pred"][m] for m in ALT_METHODS},
         "own_ge_4": items[i]["pred"]["own_ge_4"]}
        for i in PAPER_NFT_ORDER
    ])
    am_rows = []
    for rng, row in res["alternative_matching"]["accuracy"].items():
        for stat in ("exact", "mae"):
            am_rows.append({"true_state": rng, "statistic": stat, **{m: row[m][stat] for m in ALT_METHODS}})
    _write_csv(out_dir / "table_alternative_matching_summary.csv", am_rows)

    # tab:rob1
    _write_csv(out_dir / "table_robustness.csv", [
        {"nft_id": i, "true_state": items[i]["true_state"],
         **{m: items[i]["robustness"][m] for m in ROBUSTNESS_METHODS}, "mean_mu": items[i]["pred"]["mean_mu"]}
        for i in PAPER_NFT_ORDER
    ])
    rob = res["robustness"]
    rob_rows = [{"row": f"mae_range{r}", **vals} for r, vals in rob["mae_by_range"].items()]
    rob_rows.append({"row": "p_paired_t", **rob["p_paired_t"], "mean_mu": ""})
    _write_csv(out_dir / "table_robustness_summary.csv", rob_rows)

    # tab:firststage
    _write_csv(out_dir / "table_firststage.csv", [
        {"nft_id": i, "n": items[i]["n"], "retained": items[i]["retained"],
         "F_range1": items[i]["first_stage_F"][0], "F_range2": items[i]["first_stage_F"][1],
         "F_range3": items[i]["first_stage_F"][2]}
        for i in sorted(items)
    ])

    # tab:sp_replication
    _write_csv(out_dir / "table_sp_replication.csv", [
        {"nft_id": i, "true_state": items[i]["true_state"], "n": items[i]["n"],
         "mu12_pct": 100 * items[i]["mu12"], "alpha12_pct": 100 * items[i]["alpha12"],
         "sp_group": group_label(items[i]["sp_group"]), "p_one_sided": items[i]["sp_p_one_sided"]}
        for i in PAPER_NFT_ORDER
    ])

    # Figure data: the 320 estimated components and the 80 vector sums.
    comp_rows, sum_rows = [], []
    for i in PAPER_NFT_ORDER:
        means = items[i]["means"]
        for k in range(4):
            for d in range(4):
                comp_rows.append({"nft_id": i, "true_state": items[i]["true_state"], "candidate_state": k + 1,
                                  "coordinate": d + 1, "estimate": means[k, d],
                                  "class": _component_class(means[k, d])})
            sum_rows.append({"nft_id": i, "candidate_state": k + 1, "sum": float(means[k].sum()),
                             "sum_minus_one": float(means[k].sum() - 1.0)})
    _write_csv(out_dir / "figure_data" / "state_contingent_means.csv", comp_rows)
    _write_csv(out_dir / "figure_data" / "vector_sums.csv", sum_rows)
    _write_csv(out_dir / "figure_data" / "component_histogram.csv", [
        {"bin_left": left, "bin_right": round(left + 0.2, 1), "count": c} for left, c in res["histogram"].items()
    ])
    _write_csv(out_dir / "figure_data" / "validity_grid.csv", res["validity_grid"])

    # Text numbers and summaries.
    va = {k: v for k, v in res["validity"].items() if k not in ("components", "sum_errors")}
    summary = {
        "sample": res["sample"],
        "first_stage": res["first_stage"],
        "uncertainty_and_where": res["prediction_errors"]["uncertainty"],
        "constant_range2": res["constant_2"],
        "binary_sp": {k: sc[k] for k in ("correct_pmba", "correct_sp", "total_pmba", "total_sp")}
        | {"mcnemar_p_all": sc["tests"]["all"]["mcnemar_p"]},
        "validity": va,
        "alternative_matching_text": res["alternative_matching"]["text"],
    }
    _write_json(out_dir / "summary.json", summary)
    _write_json(out_dir / "values.json", flat_values(res))


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

RED, GREY, ORANGE, BLUE = "#d95c57", "#e9ecf0", "#e3a43a", "#336b97"
FRAME = "#1565b0"


def plot_distribution(res: dict, path: Path) -> None:
    """Matplotlib version of State_contingent_Vec_dist.png."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    va = res["validity"]
    comps = np.asarray(va["components"])
    sums = np.asarray(va["sum_errors"]) * 1e15
    n = comps.size

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})

    lo = np.floor(comps.min() / 0.2) * 0.2
    hi = np.ceil(comps.max() / 0.2) * 0.2
    bins = np.round(np.arange(lo, hi + 0.2001, 0.2), 1)
    groups = [
        (comps[comps < 0], "#b9604b", f"Below 0: {va['n_negative']} ({100 * va['n_negative'] / n:.1f}%)"),
        (comps[(comps >= 0) & (comps <= 1)], BLUE, f"Within [0, 1]: {va['n_within']} ({100 * va['n_within'] / n:.1f}%)"),
        (comps[comps > 1], "#d79b45", f"Above 1: {va['n_above_one']} ({100 * va['n_above_one'] / n:.1f}%)"),
    ]
    for data, color, label in groups:
        ax1.hist(data, bins=bins, color=color, edgecolor="white", label=label)
    ax1.axvspan(0, 1, color="#e8eef6", zorder=0)
    for x in (0, 1):
        ax1.axvline(x, color="#2b3a4a", ls="--", lw=1)
    ax1.set_title(f"(a) Component bounds: {n} estimates", loc="left", fontweight="bold")
    ax1.set_xlabel("Estimated state-contingent mean component")
    ax1.set_ylabel("Number of components")
    ax1.legend(frameon=False)

    edge = 0.5 * np.ceil(np.abs(sums).max() / 0.5 + 0.5)
    ax2.hist(sums, bins=np.arange(-edge - 0.25, edge + 0.26, 0.5), color=BLUE, edgecolor="white")
    ax2.axvline(0, color="#2b3a4a", ls="--", lw=1)
    ax2.set_title(f"(b) Adding up: {sums.size} state-contingent vectors", loc="left", fontweight="bold")
    ax2.set_xlabel(r"(sum of components $-$ 1) $\times 10^{15}$")
    ax2.set_ylabel("Number of vectors")
    ax2.text(0.02, 0.97, "All sums equal 1 to numerical precision\n"
             f"Maximum absolute error: {va['max_abs_sum_error']:.2e}",
             transform=ax2.transAxes, ha="left", va="top", color="#4a5562")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#eeeeee")
        ax.set_axisbelow(True)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_valid_grid(res: dict, path: Path) -> None:
    """Matplotlib version of valid_grid.png."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle

    grid = res["validity_grid"]
    colors = {"N": RED, "V": GREY, "A": ORANGE}
    n_rows = len(grid)

    fig, ax = plt.subplots(figsize=(14, 8))
    for r, row in enumerate(grid):
        for c, code in enumerate(row["cells"]):
            ax.add_patch(Rectangle((c, r), 1, 1, facecolor=colors[code], edgecolor="white", lw=1))
        k = row["true_state"] - 1
        ax.add_patch(Rectangle((4 * k + 0.03, r + 0.05), 4 - 0.06, 0.9, fill=False, edgecolor=FRAME, lw=2))

    for c in (4, 8, 12):
        ax.axvline(c, color="#6b7785", lw=1)
    prev = grid[0]["true_state"]
    for r, row in enumerate(grid):
        if row["true_state"] != prev:
            ax.axhline(r, color="#2b3a4a", lw=2)
            prev = row["true_state"]

    ax.set_xlim(0, 16)
    ax.set_ylim(n_rows, 0)
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels([f"{row['nft_id']:02d} / S{row['true_state']}" for row in grid])
    ax.set_xticks(np.arange(16) + 0.5)
    ax.set_xticklabels([str(d) for _ in range(4) for d in range(1, 5)])
    ax.xaxis.tick_top()
    for k in range(4):
        ax.text(4 * k + 2, -1.2, f"Candidate state {k + 1}", ha="center", fontweight="bold")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    va = res["validity"]
    handles = [
        Patch(facecolor=RED, label=f"< 0: {va['n_negative']}"),
        Patch(facecolor=GREY, label=f"[0,1]: {va['n_within']}"),
        Patch(facecolor=ORANGE, label=f"> 1: {va['n_above_one']}"),
        Patch(facecolor="white", edgecolor=FRAME, lw=2, label="True candidate state"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4, frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def write_all(out_dir: Path, res: dict | None = None) -> dict:
    if res is None:
        res = compute_all()
    write_tables(res, out_dir)
    plot_distribution(res, out_dir / "figures" / "state_contingent_vec_dist.png")
    plot_valid_grid(res, out_dir / "figures" / "valid_grid.png")
    return res
