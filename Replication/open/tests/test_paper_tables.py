from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from replication_open.paper_checks import run_crosscheck
from replication_open.paper_tables import (
    build_prediction_errors_table,
    build_sp_replication_table,
)


class PaperTableTests(unittest.TestCase):
    def test_prediction_error_summary_mae(self):
        t = build_prediction_errors_table()
        s = t["summary"]
        self.assertAlmostEqual(s["mae_pmba"], 1.25, places=8)
        self.assertAlmostEqual(s["mae_majority_mu"], 1.50, places=8)
        self.assertAlmostEqual(s["mae_majority_alpha"], 1.40, places=8)

    def test_sp_replication_nft2(self):
        t = build_sp_replication_table()
        rows = {r["nft_id"]: r for r in t["rows"]}
        r2 = rows[2]
        self.assertEqual(r2["n_obs"], 103)
        self.assertAlmostEqual(r2["mu12_pct"], 68.73, places=2)
        self.assertAlmostEqual(r2["alpha12_pct"], 69.93, places=2)
        self.assertEqual(r2["sp_group"], "3&4")

    def test_crosscheck_has_no_mismatches(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            rep = run_crosscheck(out)
            self.assertGreater(rep["n_matches"], 0)
            self.assertEqual(rep["n_mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
