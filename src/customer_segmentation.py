"""
customer_segmentation.py

RFM (Recency, Frequency, Monetary) customer segmentation.

RFM is a standard marketing-analytics technique used to group customers
by behavior:

- Recency:   How many days ago was the customer's last order?
             (Lower = more recently active = better)
- Frequency: How many distinct orders has the customer placed?
             (Higher = more loyal = better)
- Monetary:  How much total revenue has the customer generated?
             (Higher = more valuable = better)

Each customer is scored 1-4 (quartiles) on each dimension, and the
three scores are combined into a single segment label such as
"Champions", "At Risk", or "Lost", which is directly actionable for
a marketing or retention team.
"""

import pandas as pd


def compute_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    Compute RFM metrics and quartile scores per customer.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset with 'Customer ID', 'Order Date', 'Order ID',
        'Sales' columns.
    snapshot_date : pd.Timestamp, optional
        The reference "today" date used to compute Recency. Defaults to
        one day after the most recent order in the dataset (the usual
        convention when the dataset itself has no explicit "as of" date).

    Returns
    -------
    pd.DataFrame
        One row per customer with R, F, M raw values, their 1-4 scores,
        a combined RFM score string, and a human-readable Segment label.
    """
    if snapshot_date is None:
        snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("Customer ID")
        .agg(
            Customer_Name=("Customer Name", "first"),
            Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
        )
        .reset_index()
    )

    # Quartile scoring: for Recency, LOWER is better, so scores are reversed.
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    )
    rfm["RFM_Sum"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

    rfm["Segment"] = rfm.apply(_label_segment, axis=1)
    return rfm


def _label_segment(row) -> str:
    """
    Translate R/F/M scores into a business-friendly segment name.

    This mirrors common RFM segmentation heuristics used in industry
    (e.g. by marketing platforms like HubSpot / Klaviyo).
    """
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers"
    if r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    if r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    return "Needs Attention"


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Aggregate customer count and average monetary value per segment."""
    return (
        rfm.groupby("Segment")
        .agg(
            Customers=("Customer ID", "nunique"),
            Avg_Monetary=("Monetary", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Recency=("Recency", "mean"),
        )
        .round(2)
        .sort_values("Customers", ascending=False)
        .reset_index()
    )
