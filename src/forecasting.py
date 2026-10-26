"""
forecasting.py

Time-series forecasting of monthly sales using Holt-Winters
Exponential Smoothing (Triple Exponential Smoothing).

Why Holt-Winters instead of a heavier library like Prophet?
- It natively models both trend AND yearly seasonality, which retail
  sales data (e.g. holiday-season spikes) clearly exhibits.
- It ships inside `statsmodels`, so it keeps the project's dependency
  footprint small and easy for anyone to install and run.
- It is fast, well-documented, and a standard, defensible technique to
  discuss in a data-analyst interview.
"""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def build_monthly_series(df: pd.DataFrame) -> pd.Series:
    """
    Aggregate raw transactions into a continuous monthly Sales series.

    Returns
    -------
    pd.Series
        Indexed by month-start Timestamp, values are total Sales for
        that month. Guaranteed to have no gaps (missing months are
        filled with 0) since gaps break seasonal models.
    """
    monthly = (
        df.set_index("Order Date")["Sales"]
        .resample("MS")  # MS = Month Start frequency
        .sum()
    )
    return monthly.asfreq("MS", fill_value=0)


def forecast_sales(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """
    Fit a Holt-Winters model on historical monthly sales and forecast
    forward.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset with 'Order Date' and 'Sales' columns.
    periods : int
        Number of future months to forecast (default 6).

    Returns
    -------
    pd.DataFrame
        Columns: Date, Sales, Type ('Actual' or 'Forecast'). This shape
        is convenient for plotting actual + forecast on one chart.
    """
    monthly = build_monthly_series(df)

    model = ExponentialSmoothing(
        monthly,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit()

    forecast = model.forecast(periods)

    actual_df = monthly.reset_index()
    actual_df.columns = ["Date", "Sales"]
    actual_df["Type"] = "Actual"

    forecast_df = forecast.reset_index()
    forecast_df.columns = ["Date", "Sales"]
    forecast_df["Type"] = "Forecast"

    return pd.concat([actual_df, forecast_df], ignore_index=True)
