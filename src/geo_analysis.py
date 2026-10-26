"""
geo_analysis.py

Geographic (state-level) sales and profit analysis for the US market.

Provides:
- A US state-name -> USPS abbreviation lookup (required by Plotly's
  built-in 'USA-states' choropleth projection, which only understands
  two-letter codes, not full state names).
- An aggregation helper that summarizes Sales / Profit / Orders per state.
"""

import pandas as pd

# Standard USPS two-letter codes for all US states + DC.
# Needed because Plotly choropleth maps require this format.
US_STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate Sales, Profit, Orders and Profit Margin per US state.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset (must contain 'State', 'Sales', 'Profit',
        'Order ID' columns).

    Returns
    -------
    pd.DataFrame
        One row per state with: State, State Code, Sales, Profit,
        Orders, Profit Margin.
    """
    summary = (
        df.groupby("State")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    summary["State Code"] = summary["State"].map(US_STATE_ABBREV)
    summary["Profit Margin"] = (summary["Profit"] / summary["Sales"]).round(4)
    return summary.sort_values("Sales", ascending=False)


def top_bottom_states(df: pd.DataFrame, n: int = 5) -> dict:
    """
    Return the top-N and bottom-N states by profit.

    Useful for the 'unprofitable states' business insight: some states
    can have high sales but negative profit due to heavy discounting.
    """
    summary = state_summary(df)
    return {
        "top_profit": summary.nlargest(n, "Profit")[["State", "Sales", "Profit"]],
        "bottom_profit": summary.nsmallest(n, "Profit")[["State", "Sales", "Profit"]],
    }
