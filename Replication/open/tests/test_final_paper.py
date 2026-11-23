from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from replication_open.final_paper import compute_all
from replication_open.final_paper_checks import run_final_check, values_match


class FinalPaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = compute_all()

    def test_final_paper_has_no_mismatches(self):
        with tempfile.TemporaryDirectory() as td:
            report = run_final_check(Path(td), self.res)
        self.assertGreater(report["n_checked"], 1000)
        mismatches = [f"{m['key']}: paper={m['expected']} computed={m['got']}" for m in report["mismatches"]]
        self.assertEqual(mismatches, [])

    def test_matching_rule_detects_differences(self):
        self.assertTrue(values_match(0.048074, 0.0481, 4))
        self.assertFalse(values_match(0.048074, 0.0482, 4))
        self.assertTrue(values_match(-0.5489, -0.55, 2))
        self.assertFalse(values_match(5, 4, None))
        self.assertFalse(values_match(1, True, None))
        self.assertFalse(values_match("VVVN", "VVNV", None))


if __name__ == "__main__":
    unittest.main()
