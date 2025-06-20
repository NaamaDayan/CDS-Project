import unittest
from datetime import datetime
import pandas as pd
import numpy as np

# Assume the main implementation has been imported here
# from hematology import (
#     Gender, HemoglobinStateRange, WBCStateRange, generate_patient_state_timeline,
#     find_overlapping_states, resolve_conflicts, fill_gaps
# )
from models import WBCStateRange, HemoglobinStateRange
from patient_state_calculator import find_overlapping_states, resolve_conflicts, generate_patient_state_timeline, \
    fill_gaps


class TestHematologyInference(unittest.TestCase):
    def setUp(self):
        # Hematological Table
        wbc_intervals = pd.IntervalIndex.from_tuples([
            (0, 4000),
            (4000, 10000),
            (10000, np.inf)
        ], closed="left")

        female_hb_intervals = pd.IntervalIndex.from_tuples([
            (0, 8),
            (8, 10),
            (10, 12),
            (12, 14),
            (14, np.inf)
        ], closed="left")

        female_hematological_data = [
            ['Pancytopenia', 'Pancytopenia', 'Pancytopenia', 'Leukopenia', 'Suspected Polycytemia Vera'],
            ['Anemia', 'Anemia', 'Anemia', 'Normal', 'Polyhemia'],
            ['Suspected Leukemia', 'Suspected Leukemia', 'Suspected Leukemia', 'Leukemoid reaction', 'Suspected Polycytemia Vera']
        ]

        self.hematological_table = pd.DataFrame(female_hematological_data, index=wbc_intervals, columns=female_hb_intervals)

    def make_wbc(self, dt, val):
        return WBCStateRange(dt, val, 3, 3)

    def make_hb(self, dt, val):
        return HemoglobinStateRange(dt, val, 3, 3)

    def test_overlap_inference(self):
        wbc = self.make_wbc(datetime(2025, 1, 1, 10, 0), 5000)
        hb = self.make_hb(datetime(2025, 1, 1, 10, 0), 14.1)

        result = find_overlapping_states([wbc], [hb], self.hematological_table)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 'Polyhemia')

    def test_non_overlap_no_state(self):
        wbc = self.make_wbc(datetime(2025, 1, 1, 10, 0), 5000)
        hb = self.make_hb(datetime(2025, 1, 2, 10, 0), 14.1)  # out of overlap range

        result = find_overlapping_states([wbc], [hb], self.hematological_table)
        self.assertEqual(result, [])

    def test_conflict_resolution(self):
        dt1 = datetime(2025, 1, 1, 10, 0)
        dt2 = datetime(2025, 1, 1, 11, 0)

        state1 = (dt1, dt1 + pd.Timedelta(hours=4), 'Normal')
        state2 = (dt2, dt2 + pd.Timedelta(hours=4), 'Polyhemia')

        resolved = resolve_conflicts([state1, state2])
        self.assertEqual(len(resolved), 2)
        self.assertEqual(resolved[0][2], 'Normal')
        self.assertEqual(resolved[1][2], 'Polyhemia')
        # Check midpoint split
        self.assertEqual(resolved[0][1], resolved[1][0])

    def test_fill_gaps(self):
        dt1 = datetime(2025, 1, 1, 10, 0)
        dt2 = datetime(2025, 1, 1, 12, 0)

        intervals = [(dt1, dt1 + pd.Timedelta(hours=1), 'A'), (dt2, dt2 + pd.Timedelta(hours=1), 'B')]
        filled = fill_gaps(intervals)

        self.assertEqual(len(filled), 3)
        self.assertIsNone(filled[1][2])  # gap state

    def test_full_timeline(self):
        wbc_data = [
            self.make_wbc(datetime(2025, 6, 17, 10, 0), 5000),
            self.make_wbc(datetime(2025, 6, 17, 12, 0), 5000),
        ]

        hb_data = [
            self.make_hb(datetime(2025, 6, 17, 10, 0), 14.1),
            self.make_hb(datetime(2025, 6, 17, 12, 0), 13.5),
        ]

        timeline = generate_patient_state_timeline(wbc_data, hb_data, self.hematological_table)
        self.assertGreaterEqual(len(timeline), 2)
        self.assertEqual(timeline[0][2], 'Polyhemia')
        self.assertEqual(timeline[1][2], 'Normal')  # state changed due to newer data

if __name__ == '__main__':
    unittest.main()
