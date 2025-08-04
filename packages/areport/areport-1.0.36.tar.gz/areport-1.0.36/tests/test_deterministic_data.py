from unittest import TestCase, main

import numpy as np

from tests.deterministic_data import (
    bound_random_walk,
    geometric_daily,
    geometric_hourly,
    mock_daily,
)


class TestDeterministicData(TestCase):
    def test_bound_random_walk(self):
        n_tests = 100

        with self.assertRaises(ValueError):
            bound_random_walk(-1, 100)

        with self.assertRaises(ValueError):
            bound_random_walk(100, -100)

        with self.assertRaises(TypeError):
            bound_random_walk(100, 200, 0.3)

        with self.assertRaises(ValueError):
            bound_random_walk(100, 200, -1)

        with self.assertRaises(ValueError):
            bound_random_walk(100, 200, -1, -0.1)

        with self.assertRaises(NotImplementedError):
            bound_random_walk(100, 100)

        for _ in range(n_tests):
            start = np.random.randint(1, 100)
            end = np.random.randint(1, 100)
            min_size = np.random.randint(100, 10000)

            if start == end:
                end += np.random.choice([-1, 1], 1)

            output = bound_random_walk(start, end, min_size=min_size, trend_strength=0.01)

            self.assertEqual(output[0], start)
            self.assertEqual(output[-1], end)

            if start > end:
                # should only hit the end price once
                self.assertEqual(np.sum(output <= end), 1)

            elif end > start:
                # should only hit the end price once
                try:
                    self.assertEqual(np.sum(output >= end), 1)
                except:
                    print(output, start, end)

    def test_mock_daily(self):
        n_tests = 100

        # check bad inputs
        with self.assertRaises(ValueError):
            mock_daily(-1, 100, 100)

        with self.assertRaises(ValueError):
            mock_daily(100, -100, 100)

        with self.assertRaises(ValueError):
            mock_daily(100, 100, -100)

        with self.assertRaises(TypeError):
            mock_daily(100, 100, 0.1)

        with self.assertRaises(NotImplementedError):
            mock_daily(100, 100, 100)

        # check that the start and end is always correct
        for _ in range(n_tests):
            start = np.random.randint(1, 100)
            end = np.random.randint(1, 100)
            n_days = np.random.randint(100, 1000)

            if start == end:
                end += np.random.choice([-1, 1], 1)

            output = mock_daily(start, end, n_days)

            # start and end are correct
            self.assertEqual(output.iloc[0], start)
            self.assertEqual(output.iloc[-1], end)
            # number of days is correct
            self.assertEqual(output.shape[0], n_days)
            # index is ordered correctly
            self.assertTrue(output.index.is_monotonic_increasing)
            # index is daily
            self.assertTrue(output.equals(output.resample("d").first()))

            # the start and end should be far appart
            while abs(end - start) / start < 0.5:
                start = np.random.randint(1, 100)
                end = np.random.randint(1, 100)
                n_days = np.random.randint(100, 1000)

            # check that the trend is strong
            output = mock_daily(start, end, n_days, trend_strength=10.0)

            # start and end are correct
            self.assertEqual(output.iloc[0], start)
            self.assertEqual(output.iloc[-1], end)
            # number of days is correct
            self.assertEqual(output.shape[0], n_days)
            # index is ordered correctly
            self.assertTrue(output.index.is_monotonic_increasing)
            # index is daily
            self.assertTrue(output.equals(output.resample("d").first()))
            # mean is between the start and end
            self.assertLessEqual(output.mean(), max(start, end))
            self.assertGreaterEqual(output.mean(), min(start, end))

    def test_geometric_daily(self):
        output = geometric_daily(1, 2.7048138294215285, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 1.01**100)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)

        output = geometric_daily(1, 10, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 10)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)

        output = geometric_daily(1, 0.5, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 0.5)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)
        self.assertTrue(output.index.is_monotonic_increasing)
        # index is daily
        self.assertTrue(output.equals(output.resample("d").first()))

    def test_geometric_hourly(self):
        output = geometric_hourly(1, 2.7048138294215285, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 1.01**100)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)

        output = geometric_hourly(1, 10, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 10)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)

        output = geometric_hourly(1, 0.5, 100)
        self.assertEqual(output.iloc[0], 1)
        self.assertAlmostEqual(output.iloc[-1], 0.5)
        self.assertEqual(output.shape[0], 100)
        # number of unique values should be 2, nan + R
        self.assertEqual(output.pct_change().round(5).unique().shape[0], 2)
        self.assertTrue(output.index.is_monotonic_increasing)
        # index is daily
        self.assertFalse(output.equals(output.resample("d").first()))
        self.assertTrue(output.equals(output.resample("h").first()))


if __name__ == "__main__":
    main()
