# aplotly

## Installation

```bash
pip install areport
```

## Usage

For examples please refer to the code in the `examples` folder.

### Report

The `Report` class contains the methods for computing common metrics and storing them to files. The class is initialized with a list of portfolio values. These values should always start with the initial value of 1, otherwise the class will raise an error.
    
```python
from areport import Report

report = Report([1.0, 1.1, 1.2])
```
### ReportComparison

The `ReportComparison` class contains the methods for comparing multiple reports. The class is initialized with one `Report` that is treated as the portfolio, and a dictionary of other `Report` instances that are treated as benchmarks.

```python
from areport import ReportComparison

report_comparison = ReportComparison(report, {'benchmark1': report1, 'benchmark2': report2})
```

### Metrics

The common metrics can be retrieved using the following methods:

```python
from areport import Report

report = Report([1.0, 1.1, 1.2])
report.get_metrics()
```

The same is also possible for the `ReportComparison` class:

```python
from areport import ReportComparison

report_comparison = ReportComparison(report, {'benchmark1': report1, 'benchmark2': report2})
report_comparison.get_metrics()
```
If you want to save the metrics to a file, you can use the `metrics_to_{format}` method:

```python
from areport import Report

report = Report([1.0, 1.1, 1.2])
report.metrics_to_csv('report.csv')
report.metrics_to_json('report.json')
```

The same is also possible for the `ReportComparison` class:

```python
from areport import ReportComparison

report_comparison = ReportComparison(report, {'benchmark1': report1, 'benchmark2': report2})
report_comparison.metrics_to_csv('report_comparison.csv')
report_comparison.metrics_to_json('report_comparison.json')
```

## Using with `aplotly`

This package can be combined with the `aplotly` package to create interactive plots. The `aplotly` package is a wrapper around the `plotly` package that simplifies the creation of plots. The useful attrbutes of the `Report` class are `pf_values` and `dt_pf_values`. 
Here is an example of how to use the `aplotly` package with the `Report` class to create the performance chart.

```python
from aplotly.plots import plot_performance
from areport import Report

report = Report([1.0, 1.1, 1.2])

fig = plot_performance(
    report.performance_to_pct(report.dt_pf_values - 1)  # performance in percentage
    report.drawdown_to_pct(report.drawdown, report.dt_pf_values.index)  # drawdown in percentage
    performance_label="Test",
    drawdown_label="Test",
    xlabel="X",
)
fig.show()
```

# Metrics

Detailed documentation for the metrics can be found on [Notion](https://www.notion.so/Metrics-and-Definitions-8741dfecb227479583eba3d04253ac1d?pvs=4)