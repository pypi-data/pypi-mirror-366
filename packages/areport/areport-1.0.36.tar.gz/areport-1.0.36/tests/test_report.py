from unittest import TestCase, main

import numpy as np
import pandas as pd

from areport import Report
from tests.deterministic_data import geometric_daily, mock_daily


class TestReport(TestCase):
    def test_init(self):
        n_tests = 100

        # check that the frequency is correct when we subsample
        for _ in range(n_tests):
            rate = np.random.randint(2, 60)
            mock_pf = mock_daily(1, 2, 100).iloc[::rate]
            report = Report(mock_pf)
            self.assertTrue(report.dt_pf_values.equals(mock_pf))
            self.assertLessEqual(abs(report.freq - 365 / rate), 1)

        # try to create a report with values that doesn't start at one
        with self.assertRaises(ValueError):
            Report(mock_daily(2, 3, 100))

    def test_from_returns(self):
        n_tests = 100

        for _ in range(n_tests):
            mock_pf = mock_daily(1, np.random.uniform(low=0.1, high=100), 100)
            report = Report.from_returns(mock_pf.pct_change().fillna(0.0))
            self.assertLessEqual((report.dt_pf_values - mock_pf).abs().max(), 1e-9)
            self.assertEqual(report.freq, 365)

            # check when using timestamps instead of datetimes
            ts_mock_pf = mock_pf.copy()
            ts_mock_pf.index = [t.timestamp() for t in ts_mock_pf.index]
            report = Report(ts_mock_pf)
            self.assertTrue(report.dt_pf_values.equals(mock_pf))
            self.assertEqual(report.freq, 365)

    def test_from_balances(self):
        n_tests = 100

        for _ in range(n_tests):
            mock_pf = mock_daily(1, np.random.uniform(low=0.1, high=100), 100)
            report = Report.from_balances(mock_pf)
            self.assertLessEqual((report.dt_pf_values - mock_pf).abs().max(), 1e-9)
            self.assertEqual(report.freq, 365)

            # check when using timestamps instead of datetimes
            ts_mock_pf = mock_pf.copy()
            ts_mock_pf.index = [t.timestamp() for t in ts_mock_pf.index]
            report = Report(ts_mock_pf)
            self.assertTrue(report.dt_pf_values.equals(mock_pf))
            self.assertEqual(report.freq, 365)

        # check raising ValueError
        invalid_balances = [1, 2, 3]
        with self.assertRaises(ValueError):
            Report.from_balances(invalid_balances)

    def test_final_pnl(self):
        n_tests = 100

        # create a report using timestamps
        for _ in range(n_tests):
            end_val = np.random.randint(2, 10)
            mock_pf = mock_daily(1, end_val, 100)
            ts_mock_pf = mock_pf.copy()
            ts_mock_pf.index = [t.timestamp() for t in ts_mock_pf.index]

            report = Report(ts_mock_pf)
            self.assertTrue(report.dt_pf_values.equals(mock_pf))
            self.assertEqual(report.freq, 365)
            self.assertEqual(report.final_pnl, (end_val - 1))

        # create a report using datetimes
        for _ in range(n_tests):
            end_val = np.random.randint(2, 10)
            mock_pf = mock_daily(1, end_val, np.random.randint(10, 600))
            report = Report(mock_pf)
            self.assertTrue(report.dt_pf_values.equals(mock_pf))
            self.assertEqual(report.freq, 365)
            self.assertEqual(report.final_pnl, (end_val - 1))

    def test_annal_returns(self):
        mock_pf = mock_daily(1, 2, 365, start_time=1672531200)
        self.assertEqual(mock_pf.shape[0], 365)
        self.assertEqual(mock_pf.index[0], pd.to_datetime("2023-01-01"))
        self.assertEqual(mock_pf.index[-1], pd.to_datetime("2023-12-31"))
        report = Report(mock_pf)
        expected_series = pd.Series([1.0], index=[2023], name="return")
        self.assertTrue(report.annual_returns.equals(expected_series))

    def test_monthly_returns(self):
        mock_pf = mock_daily(1, 2, 31, start_time=1672531200)
        self.assertEqual(mock_pf.shape[0], 31)
        self.assertEqual(mock_pf.index[0], pd.to_datetime("2023-01-01"))
        self.assertEqual(mock_pf.index[-1], pd.to_datetime("2023-01-31"))
        report = Report(mock_pf)
        expected_series = pd.Series([1.0], index=["2023-1"], name="return")
        self.assertTrue(report.monthly_returns.equals(expected_series))

    def test_quarterly_returns(self):
        mock_pf = mock_daily(1, 2, 31 + 28 + 31, start_time=1672531200)
        self.assertEqual(mock_pf.shape[0], 31 + 28 + 31)
        self.assertEqual(mock_pf.index[0], pd.to_datetime("2023-01-01"))
        self.assertEqual(mock_pf.index[-1], pd.to_datetime("2023-03-31"))
        report = Report(mock_pf)
        expected_series = pd.Series([1.0], index=["2023-3"], name="return")
        self.assertTrue(report.quarterly_returns.equals(expected_series))

    def test_mtd_performance(self):
        mock_pf = geometric_daily(1, 2, 17 + 31, start_time=1671062400)
        mock_pf_daily_returns = mock_pf.pct_change()
        self.assertEqual(mock_pf.shape[0], 17 + 31)
        self.assertEqual(mock_pf.index[0], pd.to_datetime("2022-12-15"))
        self.assertEqual(mock_pf.index[-1], pd.to_datetime("2023-01-31"))
        report = Report(mock_pf)

        # check date
        self.assertTrue(report.mtd_performance.index[0] == pd.to_datetime("2022-12-31"))
        self.assertTrue(report.mtd_performance.index[-1] == pd.to_datetime("2023-01-31"))

        # test daily returns
        expected_series = mock_pf_daily_returns.loc["2023-01-01":"2023-01-31"].round(5)
        self.assertTrue(
            (report.mtd_performance + 1).pct_change().loc["2023-01-01":"2023-01-31"].round(5).equals(expected_series)
        )

        # test mtd returns
        num = 0
        for i in range(mock_pf.shape[0]):
            available_data = mock_pf.iloc[: i + 1]

            # expected return
            if mock_pf.index[i].day == 1:
                num = 1
            expected_return = (1 + mock_pf_daily_returns.iloc[-1]) ** (num) - 1
            num += 1

            # actual return
            report = Report(available_data)
            mtd_perf = report.mtd_performance

            self.assertAlmostEqual(mtd_perf.iloc[-1], expected_return)

    def test_ytd_performance(self):
        mock_pf = geometric_daily(1, 2, 17 + 31 + 28, start_time=1671062400)
        mock_pf_daily_returns = mock_pf.pct_change()
        self.assertEqual(mock_pf.shape[0], 17 + 31 + 28)
        self.assertEqual(mock_pf.index[0], pd.to_datetime("2022-12-15"))
        self.assertEqual(mock_pf.index[-1], pd.to_datetime("2023-02-28"))
        report = Report(mock_pf)

        # check date
        self.assertTrue(report.ytd_performance.index[0] == pd.to_datetime("2022-12-31"))
        self.assertTrue(report.ytd_performance.index[-1] == pd.to_datetime("2023-02-28"))

        # test daily returns
        expected_series = mock_pf_daily_returns.loc["2023-01-01":"2023-02-28"].round(5)
        self.assertTrue(
            (report.ytd_performance + 1).pct_change().loc["2023-01-01":"2023-02-28"].round(5).equals(expected_series)
        )

        # test ytd returns
        num = 0
        for i in range(mock_pf.shape[0]):
            available_data = mock_pf.iloc[: i + 1]

            # expected return
            if mock_pf.index[i].month == 1 and mock_pf.index[i].day == 1:
                num = 1
            expected_return = (1 + mock_pf_daily_returns.iloc[-1]) ** (num) - 1
            num += 1

            # actual return
            report = Report(available_data)
            ytd_perf = report.ytd_performance

            self.assertAlmostEqual(ytd_perf.iloc[-1], expected_return)


if __name__ == "__main__":
    main()
