#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from replication_open.config import DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE
from replication_open.pipeline import DEFAULT_METHODS, run_replication, write_outputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run open-source PMBA/SP replication pipeline.")
    p.add_argument("--raw-data", type=Path, default=DEFAULT_RAW_DATA)
    p.add_argument("--true-state", type=Path, default=DEFAULT_TRUE_STATE)
    p.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "outputs" / "run")
    p.add_argument(
        "--methods",
        nargs="+",
        default=DEFAULT_METHODS,
        help="Methods to run (subset of: ols_iv_c cls_iv_c ols_iv_nc cls_iv_nc ols_noiv_c cls_noiv_c)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    results = run_replication(args.raw_data, args.true_state, methods=args.methods)
    write_outputs(results, args.out_dir)
    print(f"Wrote outputs to {args.out_dir.resolve()}")


if __name__ == "__main__":
    main()
