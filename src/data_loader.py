"""
data_loader.py

Handles loading and cleaning the Superstore sales dataset.

This module centralizes all data-loading logic so that the notebook,
the Streamlit dashboard, and any future script all read the exact
same, consistently-cleaned dataset. Keeping this logic in one place
avoids duplicating (and accidentally diverging) cleaning steps across
the project.
"""

from pathlib import Path
import pandas as pd

# Resolve paths relative to this file so the functions work regardless
# of the current working directory the caller is running from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "superstore.csv"


def load_raw_data(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the raw Superstore CSV file.

    The source file is encoded in 'latin-1' (it contains characters,
    such as accented city/state names, that are not valid UTF-8).

    Parameters
    ----------
    path : Path
        Path to the CSV file. Defaults to data/superstore.csv.

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_csv(path, encoding="latin-1")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning and feature-engineering steps to the raw dataset.

    Steps performed:
    1. Parse Order Date / Ship Date as proper datetime objects.
    2. Derive calendar features used throughout the analysis
       (order month, year, day of week, quarter).
    3. Derive a Shipping Delay feature (days between order and ship date),
       useful for logistics/operations insights.
    4. Derive a Profit Margin feature (Profit / Sales), which is often
       more informative than raw profit for comparing product lines.

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe as returned by `load_raw_data`.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe, ready for analysis.
    """
    df = df.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Order Day of Week"] = df["Order Date"].dt.dayofweek

    df["Shipping Delay (Days)"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Profit Margin"] = (df["Profit"] / df["Sales"]).round(4)

    return df


def load_clean_data(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Convenience wrapper: load the raw CSV and immediately clean it."""
    return clean_data(load_raw_data(path))


if __name__ == "__main__":
    data = load_clean_data()
    print(f"Loaded {len(data):,} rows and {len(data.columns)} columns.")
    print(data.head())
