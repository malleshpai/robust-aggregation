from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List

from .config import THRESHOLD
from .data_prep import build_all_panels
from .estimators import estimate_by_method
from .predict import majority_prediction, pmba_predict, sp_prediction

DEFAULT_METHODS = [
    "ols_iv_c",
    "cls_iv_c",
    "ols_iv_nc",
    "cls_iv_nc",
    "ols_noiv_c",
    "cls_noiv_c",
]


def run_replication(raw_data_path: Path, true_state_path: Path, methods: Iterable[str] = DEFAULT_METHODS) -> dict:
    methods = list(methods)
    panels = build_all_panels(raw_data_path, true_state_path)

    prediction_rows: List[dict] = []
    sp_rows: List[dict] = []

    for nft_id in sorted(panels):
        panel = panels[nft_id]
        mu_hat = panel.beliefs.mean(axis=0)

        row = {
            "nft_id": panel.nft_id,
            "true_state": panel.true_state,
            "n_obs": panel.n_obs,
            "majority_pred": majority_prediction(mu_hat),
        }

        sp = sp_prediction(panel.beliefs, panel.beliefs_pop)
        row["sp_group"] = sp["sp_group"]

        sp_rows.append(
            {
                "nft_id": panel.nft_id,
                "true_state": panel.true_state,
                "n_obs": panel.n_obs,
                "mu12": sp["mu12"],
                "alpha12": sp["alpha12"],
                "sp_group": sp["sp_group"],
            }
        )

        for method in methods:
            est = estimate_by_method(panel, method)
            pred = pmba_predict(est.all_beta, mu_hat, threshold=THRESHOLD)
            row[f"{method}_pred"] = pred.predicted_range
            row[f"{method}_dist"] = pred.distance
            row[f"{method}_reasonable"] = pred.reasonable
            row[f"{method}_dropped_rows"] = est.dropped_rows

        prediction_rows.append(row)

    return {
        "prediction_rows": prediction_rows,
        "sp_rows": sp_rows,
        "methods": methods,
    }


def _write_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(results: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "predictions_by_method.csv", results["prediction_rows"])
    _write_csv(out_dir / "sp_replication.csv", results["sp_rows"])

    metadata = {
        "methods": results["methods"],
        "n_nfts": len(results["prediction_rows"]),
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
