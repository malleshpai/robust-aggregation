#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from replication_open.paper_tables import write_paper_tables

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    out_dir = PROJECT_ROOT / "outputs" / "tables"
    write_paper_tables(out_dir)
    print(f"Wrote paper tables to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
