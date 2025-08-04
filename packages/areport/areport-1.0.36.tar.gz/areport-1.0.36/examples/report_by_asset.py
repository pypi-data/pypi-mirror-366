import pandas as pd
from areport import Report

# Create a report
pf_values = pd.read_csv('pf_values.csv', index_col=0)
exposures = pd.read_csv('exposure.csv', index_col=0)

pf_values.index = pd.to_datetime(pf_values.index)
pf_values.index = [x.timestamp() for x in pf_values.index]

report = Report(pf_values.squeeze())
monthly_returns = report.monthly_return_by_asset(exposures.shift(1))
monthly_returns.to_csv("monthly_returns.csv")

report.monthly_pf_values_to_csv(file_name="monthly_pf_values.csv")
report.daily_pf_values_to_csv(file_name="daily_pf_values.csv")
report.annual_pf_values_to_csv(file_name="annual_pf_values.csv")

participation = report.participation_by_asset_ytd(exposures.shift(1))
print(participation)
print(report.daily_exposure(exposures))
