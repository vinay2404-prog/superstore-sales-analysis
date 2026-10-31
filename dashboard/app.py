
"""
Superstore Sales Analytics
Native Streamlit dashboard with default Plotly chart styling.

Run from project root:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. PROJECT IMPORTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_clean_data
from src import sales_analysis as sa
from src import customer_segmentation as cs
from src import forecasting as fc
from src import geo_analysis as ga


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 3. CHART FUNCTION
# ============================================================

def chart(fig, height=380, key=None):
    """Render Plotly charts using default styling."""

    fig.update_layout(height=height)

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displaylogo": False,
            "responsive": True,
        },
        key=key,
    )


# ============================================================
# 4. DATA LOADING
# ============================================================

@st.cache_data
def get_data() -> pd.DataFrame:
    return load_clean_data()


df = get_data()

if df.empty:
    st.error(
        "The Superstore dataset is empty. Check your data source."
    )
    st.stop()


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 Superstore Analytics")

    st.caption("Sales intelligence platform")

    st.divider()

    st.subheader("Workspace")

    st.header("Filters")

    st.caption(
        "Refine the data shown across your dashboard."
    )

    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    date_range = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )

    st.divider()

    regions = st.multiselect(
        "Region",
        options=sorted(df["Region"].dropna().unique()),
        default=sorted(df["Region"].dropna().unique()),
        placeholder="Select regions",
    )

    categories = st.multiselect(
        "Category",
        options=sorted(df["Category"].dropna().unique()),
        default=sorted(df["Category"].dropna().unique()),
        placeholder="Select categories",
    )

    segments = st.multiselect(
        "Customer Segment",
        options=sorted(df["Segment"].dropna().unique()),
        default=sorted(df["Segment"].dropna().unique()),
        placeholder="Select customer segments",
    )

    st.divider()

    st.subheader("About")

    st.write(
        "Explore sales performance, profitability, customer "
        "behavior, geographic trends, and future revenue."
    )

    st.divider()

    st.caption("SUPERSTORE · ANALYTICS V1.0")


# ============================================================
# 6. FILTER DATA
# ============================================================

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])

    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

else:

    start_date = pd.Timestamp(min_date)

    end_date = (
        pd.Timestamp(max_date)
        + pd.Timedelta(days=1)
    )


filtered = df[
    (df["Order Date"] >= start_date)
    & (df["Order Date"] < end_date)
    & (df["Region"].isin(regions))
    & (df["Category"].isin(categories))
    & (df["Segment"].isin(segments))
].copy()


if filtered.empty:

    st.warning(
        "No data matches the selected filters. "
        "Please adjust your date range or selections."
    )

    st.stop()


# ============================================================
# 7. PAGE HEADER
# ============================================================

st.title("Sales Dashboard")

st.write(
    "Monitor business performance, discover customer insights, "
    "and explore trends across your retail business."
)

st.success("Analytics dashboard active")

st.divider()


# ============================================================
# 8. KPI CARDS
# ============================================================

kpis = sa.kpi_summary(filtered)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Sales",
        f"${kpis['total_sales']:,.0f}",
        help="Total sales for the selected filters.",
    )

with col2:
    st.metric(
        "Total Profit",
        f"${kpis['total_profit']:,.0f}",
        help="Total profit for the selected filters.",
    )

with col3:
    st.metric(
        "Profit Margin",
        f"{kpis['overall_profit_margin'] * 100:.1f}%",
        help="Overall profit margin for the selected data.",
    )

with col4:
    st.metric(
        "Orders",
        f"{kpis['total_orders']:,}",
        help="Order count returned by your analytics module.",
    )

with col5:
    st.metric(
        "Avg. Order Value",
        f"${kpis['avg_order_value']:,.0f}",
        help="Average order value for the selected data.",
    )


st.divider()


# ============================================================
# 9. ANALYTICS TABS
# ============================================================

tab_trends, tab_products, tab_customers, tab_geo, tab_forecast = (
    st.tabs(
        [
            "📈 Trends",
            "📦 Products",
            "👥 Customers",
            "🗺️ Geography",
            "🔮 Forecast",
        ]
    )
)


# ============================================================
# TAB 1 — SALES TRENDS
# ============================================================

with tab_trends:

    st.header("Sales & Profit Trends")

    st.caption(
        "Track monthly sales and profitability across "
        "the selected period."
    )

    ts = sa.yearly_monthly_trend(filtered)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ts["Year-Month"],
            y=ts["Sales"],
            name="Sales",
            mode="lines",
            fill="tozeroy",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ts["Year-Month"],
            y=ts["Profit"],
            name="Profit",
            mode="lines",
        )
    )

    fig.update_layout(
        hovermode="x unified",
    )

    chart(
        fig,
        height=420,
        key="sales_profit_trend",
    )

    st.divider()

    st.subheader("Discount vs. Profitability")

    st.caption(
        "Explore the relationship between discount levels "
        "and profit margins."
    )

    disc = sa.discount_profit_relationship(filtered)

    fig2 = px.bar(
        disc,
        x="Discount Bucket",
        y="Avg_Profit_Margin",
        labels={
            "Discount Bucket": "Discount range",
            "Avg_Profit_Margin": "Average profit margin",
        },
    )

    chart(
        fig2,
        height=360,
        key="discount_profit",
    )


# ============================================================
# TAB 2 — PRODUCTS
# ============================================================

with tab_products:

    st.header("Product Performance")

    st.caption(
        "Understand how product categories contribute "
        "to sales and profit."
    )

    cat = sa.by_category(filtered)

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("Sales by Category")

        fig3 = px.pie(
            cat,
            names="Category",
            values="Sales",
            hole=0.65,
        )

        chart(
            fig3,
            height=350,
            key="sales_by_category",
        )

    with c2:

        st.subheader("Profit by Category")

        fig4 = px.pie(
            cat,
            names="Category",
            values="Profit",
            hole=0.65,
        )

        chart(
            fig4,
            height=350,
            key="profit_by_category",
        )

    st.divider()

    st.subheader("Sales & Profit by Sub-Category")

    st.caption(
        "Compare sales and profit across individual "
        "product sub-categories."
    )

    subcat = sa.by_subcategory(filtered)

    fig5 = go.Figure()

    fig5.add_trace(
        go.Bar(
            x=subcat["Sub-Category"],
            y=subcat["Sales"],
            name="Sales",
        )
    )

    fig5.add_trace(
        go.Bar(
            x=subcat["Sub-Category"],
            y=subcat["Profit"],
            name="Profit",
        )
    )

    fig5.update_layout(
        barmode="group",
    )

    chart(
        fig5,
        height=440,
        key="subcategory_performance",
    )

    st.divider()

    st.subheader("Top 10 Products by Sales")

    st.caption(
        "Products ranked by sales using your existing analysis module."
    )

    top = sa.top_products(filtered, n=10)

    st.dataframe(
        top,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# TAB 3 — CUSTOMER SEGMENTATION
# ============================================================

with tab_customers:

    st.header("Customer Intelligence")

    st.caption(
        "RFM analysis explores customer purchasing behavior "
        "using Recency, Frequency, and Monetary value."
    )

    rfm = cs.compute_rfm(filtered)

    seg_summary = cs.segment_summary(rfm)

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("Customers by Segment")

        fig6 = px.bar(
            seg_summary,
            x="Segment",
            y="Customers",
            color="Segment",
            labels={
                "Segment": "Customer segment",
                "Customers": "Number of customers",
            },
        )

        chart(
            fig6,
            height=390,
            key="customer_segments",
        )

    with c2:

        st.subheader("Frequency vs. Monetary Value")

        fig7 = px.scatter(
            rfm,
            x="Frequency",
            y="Monetary",
            color="Segment",
            size="Recency",
            hover_data=["Customer_Name"],
            labels={
                "Frequency": "Purchase frequency",
                "Monetary": "Monetary value ($)",
                "Recency": "Recency",
            },
        )

        chart(
            fig7,
            height=390,
            key="customer_scatter",
        )

    st.divider()

    st.subheader("Customer Segment Summary")

    st.dataframe(
        seg_summary,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# TAB 4 — GEOGRAPHY
# ============================================================

with tab_geo:

    st.header("Geographic Performance")

    st.caption(
        "Explore differences in sales and profitability across US states."
    )

    metric = st.radio(
        "Map metric",
        ["Sales", "Profit"],
        horizontal=True,
    )

    geo = ga.state_summary(filtered)

    fig8 = px.choropleth(
        geo,
        locations="State Code",
        locationmode="USA-states",
        color=metric,
        scope="usa",
        hover_name="State",
        labels={
            "State Code": "State",
            metric: metric,
        },
    )

    chart(
        fig8,
        height=530,
        key="state_map",
    )

    st.divider()

    st.subheader("State Profitability Rankings")

    top_bottom = ga.top_bottom_states(
        filtered,
        n=5,
    )

    c1, c2 = st.columns(2)

    with c1:

        st.success("↑ Top 5 States by Profit")

        st.dataframe(
            top_bottom["top_profit"],
            width="stretch",
            hide_index=True,
        )

    with c2:

        st.error("↓ Bottom 5 States by Profit")

        st.dataframe(
            top_bottom["bottom_profit"],
            width="stretch",
            hide_index=True,
        )


# ============================================================
# TAB 5 — SALES FORECAST
# ============================================================

with tab_forecast:

    st.header("Sales Forecast")

    st.caption(
        "Explore projected sales based on your historical order data."
    )

    c1, c2 = st.columns([1, 2])

    with c1:

        horizon = st.slider(
            "Months to forecast",
            min_value=3,
            max_value=12,
            value=6,
            step=1,
        )

    with c2:

        st.subheader("Forecast configuration")

        st.write(
            f"Forecast horizon: **{horizon} months**"
        )

        st.write(
            "Model: **Holt-Winters**"
        )

    # Use full history to preserve the original forecast behavior.
    forecast_df = fc.forecast_sales(
        df,
        periods=horizon,
    )

    fig9 = px.line(
        forecast_df,
        x="Date",
        y="Sales",
        color="Type",
        labels={
            "Date": "Date",
            "Sales": "Sales ($)",
            "Type": "Series",
        },
    )

    chart(
        fig9,
        height=480,
        key="sales_forecast",
    )

    st.divider()

    st.subheader("Forecast Data")

    st.dataframe(
        forecast_df,
        width="stretch",
        hide_index=True,
    )

    st.info(
        "The forecast uses the full order history, regardless of "
        "the sidebar filters, to preserve the historical time series. "
        "Predictions are estimates and are not guaranteed future results."
    )


# ============================================================
# 10. FOOTER
# ============================================================

st.divider()

st.caption("Superstore Analytics · Sales Intelligence Platform")

st.caption(
    "Data source: Sample Superstore dataset"
)
