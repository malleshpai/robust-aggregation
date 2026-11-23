from __future__ import annotations

import unittest

from replication_open.config import DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE
from replication_open.data_prep import build_all_panels
from replication_open.pipeline import run_replication


class PipelineSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panels = build_all_panels(DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE)

    def test_panel_sample_sizes(self):
        expected_n = {
            1: 102, 2: 103, 3: 101, 4: 100, 5: 101,
            6: 100, 7: 97, 8: 96, 9: 93, 10: 97,
            11: 99, 12: 101, 13: 102, 14: 98, 15: 100,
            16: 100, 17: 94, 18: 99, 19: 104, 20: 103,
        }
        got = {k: v.n_obs for k, v in self.panels.items()}
        self.assertEqual(got, expected_n)

    def test_sp_nft1_values(self):
        p1 = self.panels[1]
        mu12 = float(p1.beliefs.mean(axis=0)[0] + p1.beliefs.mean(axis=0)[1])
        a12 = float(p1.beliefs_pop.mean(axis=0)[0] + p1.beliefs_pop.mean(axis=0)[1])
        self.assertAlmostEqual(mu12, 0.6593, places=4)
        self.assertAlmostEqual(a12, 0.6462, places=4)

    def test_ols_iv_c_predictions_match_reference_column(self):
        # Reference: robustness table column "Regression With Intercept - OLS"
        expected = {
            1: 3, 2: 1, 3: 2, 4: 1, 5: 1,
            6: 4, 7: 1, 8: 3, 9: 1, 10: 4,
            11: 1, 12: 4, 13: 2, 14: 1, 15: 1,
            16: 1, 17: 1, 18: 2, 19: 1, 20: 1,
        }
        res = run_replication(DEFAULT_RAW_DATA, DEFAULT_TRUE_STATE, methods=["ols_iv_c"])
        got = {r["nft_id"]: r["ols_iv_c_pred"] for r in res["prediction_rows"]}
        self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
