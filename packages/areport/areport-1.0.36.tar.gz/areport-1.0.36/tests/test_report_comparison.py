import random
from unittest import TestCase, main

import pandas as pd

from areport import Report, ReportComparison
from tests.deterministic_data import geometric_daily


class TestCompareReports(TestCase):
    def test_input(self):
        """Test multiple benckmarks input
        Input: portfolio and benchmark series with similar start and end value
        Expected output: the input and output should be the same"""
        n = 10

        for i in range(n):
            end_value = random.randint(1, 100)
            mock_report = geometric_daily(1, end_value, 100, timestamp_index=True)
            mock_report = Report(mock_report)
            for indx in range(i + 1):
                mock_benchmark = geometric_daily(1, end_value, 100, timestamp_index=True)
                mock_benchmark = Report(mock_benchmark)
                benchmark_dict = {str(indx): mock_benchmark}

            report = ReportComparison(mock_report, benchmark_dict)
            self.assertTrue(report.pf_report.dt_pf_values.equals(mock_report.dt_pf_values))
            for bm in benchmark_dict.values():
                self.assertTrue(report.pf_report.dt_pf_values.equals(bm.dt_pf_values))

    def test_get_benchmark_metrics(self):
        """Test benchmark metrics
        Input: portfolio and benchmark series with similar start and end value
        Expected output: 0 batting average, 1 correlation, 0 alpha, 1 beta"""
        mock_report = geometric_daily(1, 2, 32, start_time=1672444800)  # 31 Dec 2022 - 31 Jan 2023
        mock_benchmark1 = geometric_daily(2, 4, 32, start_time=1672444800)
        mock_benchmark2 = geometric_daily(3, 6, 32, start_time=1672444800)

        mock_report = Report(mock_report / mock_report.iloc[0])
        mock_benchmark1 = Report(mock_benchmark1 / mock_benchmark1.iloc[0])
        mock_benchmark2 = Report(mock_benchmark2 / mock_benchmark2.iloc[0])

        report = ReportComparison(
            mock_report,
            {
                "benchmark1": mock_benchmark1,
                "benchmark2": mock_benchmark2,
            },
        )
        expected_df = pd.DataFrame(
            {
                "batting_average": [0.0, 0.0],
                "pearson_correlation": [1.0, 1.0],
                "alpha": [0.0, 0.0],
                "beta": [1.0, 1.0],
            },
            index=["benchmark1", "benchmark2"],
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(report.get_benchmark_metrics(), index=["benchmark1", "benchmark2"]),
            expected_df,
        )

    def test_get_benchmark_monthly_returns(self):
        """Test portfolio and multiple benchmarks monthly returns table
        Input: portfolio and benchmark series with similar percentage return from 31 Dec 2022 to 31 Jan 2023
        Expected output: 0% return for Dec 2022 and 100% return for Jan 2023"""
        mock_report = geometric_daily(1, 2, 32, start_time=1672444800)  # 31 Dec 2022 - 31 Jan 2023
        mock_benchmark1 = geometric_daily(2, 4, 32, start_time=1672444800)
        mock_benchmark2 = geometric_daily(3, 6, 32, start_time=1672444800)

        mock_report = Report(mock_report / mock_report.iloc[0])
        mock_benchmark1 = Report(mock_benchmark1 / mock_benchmark1.iloc[0])
        mock_benchmark2 = Report(mock_benchmark2 / mock_benchmark2.iloc[0])

        report = ReportComparison(
            mock_report,
            {
                "benchmark1": mock_benchmark1,
                "benchmark2": mock_benchmark2,
            },
        )

        expected_df = pd.DataFrame(
            {"Portfolio": [0.0, 1.0], "benchmark1": [0.0, 1.0], "benchmark2": [0.0, 1.0]}, index=["2022-12", "2023-1"]
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(report.get_benchmark_monthly_returns(), index=["Portfolio", "benchmark1", "benchmark2"]).T,
            expected_df,
        )

    def test_get_benchmark_annual_returns(self):
        """Test portfolio and multiple benchmarks annual returns table
        Input: portfolio and benchmark series with similar percentage return from 31 Dec 2022 to 31 Dec 2023
        Expected output: 0% return for 2022 and 100% return for 2023"""
        mock_report = geometric_daily(1, 2, 365, start_time=1672444800)  # 31 Dec 2022 - 31 Dec 2023
        mock_benchmark1 = geometric_daily(2, 4, 365, start_time=1672444800)
        mock_benchmark2 = geometric_daily(3, 6, 365, start_time=1672444800)

        mock_report = Report(mock_report / mock_report.iloc[0])
        mock_benchmark1 = Report(mock_benchmark1 / mock_benchmark1.iloc[0])
        mock_benchmark2 = Report(mock_benchmark2 / mock_benchmark2.iloc[0])

        report = ReportComparison(
            mock_report,
            {
                "benchmark1": mock_benchmark1,
                "benchmark2": mock_benchmark2,
            },
        )

        expected_df = pd.DataFrame(
            {"Portfolio": [0.0, 1.0], "benchmark1": [0.0, 1.0], "benchmark2": [0.0, 1.0]}, index=[2022, 2023]
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(report.get_benchmark_annual_returns(), index=["Portfolio", "benchmark1", "benchmark2"]).T,
            expected_df,
        )

    def test_get_benchmark_trailing_returns(self):
        """Test portfolio and multiple benchmarks trailing cagr table
        Input: portfolio and benchmark series with similar percentage return from 31 Dec 2022 to 31 Dec 2023
        Expected output: 100% return for every trailing periods"""
        mock_report = geometric_daily(1, 2, 365, start_time=1672444800)  # 31 Dec 2022 - 31 Dec 2023
        mock_benchmark1 = geometric_daily(2, 4, 365, start_time=1672444800)
        mock_benchmark2 = geometric_daily(3, 6, 365, start_time=1672444800)

        mock_report = Report(mock_report / mock_report.iloc[0])
        mock_benchmark1 = Report(mock_benchmark1 / mock_benchmark1.iloc[0])
        mock_benchmark2 = Report(mock_benchmark2 / mock_benchmark2.iloc[0])

        report = ReportComparison(
            mock_report,
            {
                "benchmark1": mock_benchmark1,
                "benchmark2": mock_benchmark2,
            },
        )

        expected_df = pd.DataFrame(
            {
                "Portfolio": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "benchmark1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "benchmark2": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            },
            index=[
                "10 years returns",
                "5 years returns",
                "3 years returns",
                "1 year returns",
                "6 months returns",
                "3 months returns",
            ],
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(report.get_benchmark_trailing_cagr(), index=["Portfolio", "benchmark1", "benchmark2"]).T,
            expected_df,
        )


if __name__ == "__main__":
    main()
