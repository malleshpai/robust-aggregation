#!/usr/bin/env python3
"""Recompute every empirical number in the final paper and redraw its two appendix figures.

Writes CSV/JSON tables to outputs/final_paper/ and figures to outputs/final_paper/figures/.
"""
from __future__ import annotations

from pathlib import Path

from replication_open.final_paper_outputs import write_all

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    out_dir = PROJECT_ROOT / "outputs" / "final_paper"
    write_all(out_dir)
    print(f"Wrote final-paper outputs to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
