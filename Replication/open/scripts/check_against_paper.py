#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from replication_open.paper_checks import run_crosscheck

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    out_dir = PROJECT_ROOT / "outputs" / "tables"
    report = run_crosscheck(out_dir)
    print(f"Cross-check complete. matches={report['n_matches']} mismatches={report['n_mismatches']}")
    print(f"Report: {(out_dir / 'paper_crosscheck_report.md').resolve()}")


if __name__ == "__main__":
    main()
