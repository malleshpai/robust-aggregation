#!/usr/bin/env python3
"""Compare recomputed values with the numbers printed in the final paper (paper/main.tex).

Prints matches and mismatches, writes outputs/final_paper/final_paper_check.{md,json},
and exits with status 1 if anything does not match.
"""
from __future__ import annotations

import sys
from pathlib import Path

from replication_open.final_paper_checks import run_final_check

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    out_dir = PROJECT_ROOT / "outputs" / "final_paper"
    report = run_final_check(out_dir)
    for m in report["mismatches"]:
        print(f"MISMATCH {m['key']}: paper={m['expected']} computed={m['got']}")
    print(f"Final-paper check: checked={report['n_checked']} "
          f"matches={report['n_matches']} mismatches={report['n_mismatches']}")
    print(f"Report: {(out_dir / 'final_paper_check.md').resolve()}")
    return 1 if report["n_mismatches"] else 0


if __name__ == "__main__":
    sys.exit(main())
