from areport import Report
from typing import Union
import pandas as pd
import numpy as np
from time import time

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

    return series


# Create a report
pf_values = geometric_daily(start_price=1, end_price=2, n_days=900)
_pf_values = pd.Series(np.ones(len(pf_values)), index=pf_values.index)
_pf_values.iloc[::7] = pf_values.iloc[::7]
pf_values = _pf_values
# pf_values.iloc[::1] = 1.0

report = Report(pf_values)

report.print_metrics()
report.metrics_to_csv(file_name='report_metrics.csv')
report.daily_pf_values_to_csv(file_name='daily_pf_values.csv')
report.daily_returns_to_csv(file_name='daily_returns.csv')
report.daily_report_to_csv(file_name='daily_report.csv')
report.monthly_report_to_csv(file_name='monthly_report.csv')