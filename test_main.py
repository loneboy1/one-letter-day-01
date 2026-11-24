#!/usr/bin/env python3
"""Tests for the One Letter for Your Day entry (main.py).

Run:  python3 test_main.py
"""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main


class TestOutput(unittest.TestCase):
    def run_entry(self, out_path):
        env = dict(os.environ, ENTRY_OUTPUT=out_path)
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(out_path, "rb") as f:
            return f.read()

    def test_output_is_exactly_one_byte_v(self):
        """The gate requires exactly 1 character: one byte, no newline."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "entry.txt")
            data = self.run_entry(out)
            self.assertEqual(data, b"V")

    def test_two_runs_byte_identical(self):
        """Determinism: the grader runs the program twice; both must agree."""
        with tempfile.TemporaryDirectory() as tmp:
            first = self.run_entry(os.path.join(tmp, "a.txt"))
            second = self.run_entry(os.path.join(tmp, "b.txt"))
            self.assertEqual(first, second)

    def test_output_is_a_single_ascii_letter(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = self.run_entry(os.path.join(tmp, "entry.txt"))
            self.assertEqual(len(data), 1)
            self.assertTrue(b"A" <= data <= b"Z")


class TestScorer(unittest.TestCase):
    def test_chooses_v_under_brief_weights(self):
        self.assertEqual(main.choose_letter(), "V")

    def test_v_beats_rivals_by_total(self):
        self.assertGreater(main.total_score("V"), main.total_score("T"))
        self.assertGreater(main.total_score("V"), main.total_score("F"))
        self.assertGreater(main.total_score("V"), main.total_score("M"))

    def test_v_is_top_three_under_every_weight_permutation(self):
        """No re-weighting of vivid/funny/true drops V out of the top three."""
        ranks = main.sensitivity_rank()
        self.assertEqual(len(ranks), 6)
        for weights, rank in ranks.items():
            self.assertLessEqual(rank, 3, f"weights {weights}: V ranks #{rank}")
        firsts = sum(1 for rank in ranks.values() if rank == 1)
        self.assertEqual(firsts, 4)

    def test_v_first_under_brief_weights_in_sensitivity(self):
        ranks = main.sensitivity_rank()
        self.assertEqual(ranks[(4, 3, 2)], 1)

    def test_flooded_z_cannot_win(self):
        """448 declared copies cap Z's penalty and sink it below V."""
        self.assertEqual(main.saturation_penalty("Z"), main.PENALTY_CAP)
        self.assertLess(main.total_score("Z"), main.total_score("V"))

    def test_all_26_letters_scored(self):
        self.assertEqual(len(main.CANDIDATES), 26)
        self.assertEqual(set(main.CANDIDATES), set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.assertEqual(set(main.FIELD_TALLY), set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        for letter in main.CANDIDATES:
            self.assertTrue(0 <= main.raw_score(letter) <= 90)

    def test_ranking_is_deterministic(self):
        self.assertEqual(main.rank_letters(), main.rank_letters())

    def test_unknown_count_letters_use_the_median_prior(self):
        for letter in main.UNKNOWN_COUNT_LETTERS:
            self.assertEqual(main.FIELD_TALLY[letter], main.MEDIAN_PRIOR)

    def test_explain_runs(self):
        result = subprocess.run(
            [sys.executable, "main.py", "--explain"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("V", result.stdout)
        self.assertIn("vampire", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
