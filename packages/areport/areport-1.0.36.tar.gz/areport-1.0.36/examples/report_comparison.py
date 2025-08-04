from areport import Report, ReportComparison
# from tests.deterministic_data import geometric_daily
import pandas as pd
import numpy as np
from time import time
from typing import Union


def geometric_daily(
    start_price: float,
    end_price: float,
    n_days: int,
    start_time: Union[float, None] = None,
    timestamp_index: bool = False,
):
    r = (end_price / start_price) ** (1 / (n_days - 1))

    if start_time is None:
        end = pd.to_datetime(time(), unit="s").floor("1d")
        start = end - pd.DateOffset(days=n_days - 1)
    else:
        start = pd.to_datetime(start_time, unit="s")
        end = start + pd.DateOffset(days=n_days - 1)

    date_range = pd.date_range(start, end, freq="d")

    price = np.array([start_price * r**n for n in range(n_days)])
    series = pd.Series(price, index=date_range)

    if timestamp_index:
        series.index = [t.timestamp() for t in series.index]

    # add some noise
    series = series * np.random.normal(1, 0.05, size=series.shape)
    series.iloc[0] = 1

    return series


# Create a report
portfolio_pf_values = geometric_daily(start_price=1, end_price=1.5, n_days=90)
benchmark_pf_values = geometric_daily(start_price=1, end_price=1.0, n_days=90)
comparison = ReportComparison(report=Report(portfolio_pf_values), benchmark_reports={'bm_1': Report(benchmark_pf_values)})

comparison.print_metrics()
comparison.metrics_to_csv(file_name='report_comparison_metrics.csv')
comparison.benchmark_daily_report_to_csv(file_name='benchmark_daily_report.csv')
comparison.benchmark_monthly_report_to_csv(file_name='benchmark_monthly_report.csv')
comparison.benchmark_annual_report_to_csv(file_name='benchmark_annual_report.csv')
comparison.benchmark_monthly_returns_to_csv(file_name='benchmark_monthly_returns.csv')
comparison.benchmark_annual_returns_to_csv(file_name='benchmark_annual_returns.csv')
comparison.benchmark_daily_returns_to_csv(file_name='benchmark_daily_returns.csv')
comparison.benchmark_daily_pf_values_to_csv(file_name='benchmark_daily_pf_values.csv')
comparison.benchmark_monthly_pf_values_to_csv(file_name='benchmark_monthly_pf_values.csv', lookback=2)
comparison.benchmark_annual_pf_values_to_csv(file_name='benchmark_annual_pf_values.csv')
