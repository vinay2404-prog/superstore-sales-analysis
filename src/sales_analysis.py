"""
sales_analysis.py

Core sales & profit aggregation functions shared by the notebook and
the Streamlit dashboard. Each function returns a tidy DataFrame ready
to be plotted directly with Plotly.
"""

import pandas as pd


def kpi_summary(df: pd.DataFrame) -> dict:
    """High-level KPIs shown at the top of any report/dashboard."""
    return {
        "total_sales": df["Sales"].sum(),
        "total_profit": df["Profit"].sum(),
        "total_orders": df["Order ID"].nunique(),
        "total_customers": df["Customer ID"].nunique(),
        "avg_order_value": df.groupby("Order ID")["Sales"].sum().mean(),
        "overall_profit_margin": df["Profit"].sum() / df["Sales"].sum(),
    }


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Sales & Profit trend by calendar month (aggregated across all years)."""
    return (
        df.groupby(["Order Month", "Order Month Name"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
        .sort_values("Order Month")
    )


def yearly_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Sales & Profit trend by year-month, useful for spotting real growth over time."""
    ts = df.copy()
    ts["Year-Month"] = ts["Order Date"].dt.to_period("M").dt.to_timestamp()
    return (
        ts.groupby("Year-Month")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Category").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
    ).reset_index()


def by_subcategory(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Sub-Category").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
    ).reset_index().sort_values("Sales", ascending=False)


def by_segment(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("Segment").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    ).reset_index()
    summary["Sales_to_Profit_Ratio"] = (summary["Sales"] / summary["Profit"]).round(2)
    return summary


def discount_profit_relationship(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bucket orders by discount level and compute average profit margin
    per bucket. This directly answers a key business question:
    "At what discount level do we start losing money?"
    """
    bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    labels = ["0%", "1-10%", "11-20%", "21-30%", "31-40%", "41-50%", "50%+"]
    tmp = df.copy()
    tmp["Discount Bucket"] = pd.cut(tmp["Discount"], bins=bins, labels=labels)
    return (
        tmp.groupby("Discount Bucket", observed=True)
        .agg(Avg_Profit_Margin=("Profit Margin", "mean"), Orders=("Order ID", "nunique"))
        .reset_index()
    )


def top_products(df: pd.DataFrame, n: int = 10, by: str = "Sales") -> pd.DataFrame:
    return (
        df.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .reset_index()
        .nlargest(n, by)
    )


def shipping_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Average shipping delay per Ship Mode -- an operations/logistics insight."""
    return (
        df.groupby("Ship Mode")
        .agg(
            Avg_Delay_Days=("Shipping Delay (Days)", "mean"),
            Orders=("Order ID", "nunique"),
        )
        .round(2)
        .reset_index()
        .sort_values("Avg_Delay_Days")
    )
