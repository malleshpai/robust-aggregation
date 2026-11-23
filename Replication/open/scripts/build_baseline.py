#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

from replication_open.config import DEFAULT_LEGACY_TXT, DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE
from replication_open.legacy_txt_parser import parse_legacy_output
from replication_open.pipeline import run_replication, write_outputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    out_dir = PROJECT_ROOT / "outputs" / "baseline"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Freeze legacy TXT output as machine-readable CSV.
    legacy_rows = parse_legacy_output(DEFAULT_LEGACY_TXT)
    _write_csv(out_dir / "legacy_pilot_from_txt.csv", legacy_rows)

    # 2) Run deterministic open-source pipeline and store baseline outputs.
    results = run_replication(DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE)
    write_outputs(results, out_dir / "open_pipeline")

    # 3) Side-by-side comparison (legacy pilot vs open no-IV OLS column).
    open_index = {r["nft_id"]: r for r in results["prediction_rows"]}
    comparison = []
    for r in legacy_rows:
        nft_id = r["nft_id"]
        o = open_index[nft_id]
        comparison.append(
            {
                "nft_id": nft_id,
                "true_state": r["true_state"],
                "legacy_pmba_pred": r["pmba_pred_legacy"],
                "open_ols_noiv_c_pred": o["ols_noiv_c_pred"],
                "legacy_sp_group": r["sp_group_legacy"],
                "open_sp_group": o["sp_group"],
                "legacy_majority": r["majority_pred_legacy"],
                "open_majority": o["majority_pred"],
            }
        )

    _write_csv(out_dir / "legacy_vs_open_comparison.csv", comparison)
    print(f"Wrote baseline artifacts to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
