"""
Superstore Sales Analytics
Shadcn-inspired dark dashboard with colorful Plotly visualizations.

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
# PROJECT IMPORTS
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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    "background": "#09090b",
    "card": "#111113",
    "border": "#27272a",
    "text": "#fafafa",
    "muted": "#a1a1aa",
    "indigo": "#818cf8",
    "blue": "#3b82f6",
    "cyan": "#06b6d4",
    "green": "#22c55e",
    "amber": "#f59e0b",
    "pink": "#ec4899",
    "purple": "#a78bfa",
    "orange": "#f97316",
    "teal": "#14b8a6",
    "red": "#ef4444",
}

PALETTE = [
    COLORS["indigo"],
    COLORS["cyan"],
    COLORS["green"],
    COLORS["amber"],
    COLORS["pink"],
    COLORS["purple"],
    COLORS["orange"],
    COLORS["teal"],
    COLORS["red"],
    COLORS["blue"],
]


# ============================================================
# SHADCN-INSPIRED CSS
# ============================================================

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet">

    <style>
    :root {
        --background: #09090b;
        --card: #111113;
        --border: #27272a;
        --foreground: #fafafa;
        --muted: #a1a1aa;
        --radius: 10px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: var(--background);
        color: var(--foreground);
    }

    [data-testid="stHeader"] {
        background: rgba(9, 9, 11, 0.95);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1600px;
        padding: 2rem 2.2rem 3rem 2.2rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: #0d0d0f;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #fafafa;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    [data-testid="stSidebar"] label {
        color: #d4d4d8 !important;
        font-size: 0.83rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: #111113;
        border-color: #27272a;
        border-radius: 7px;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #27272a;
        border: 1px solid #3f3f46;
    }

    [data-testid="stSidebar"] hr {
        border-color: #27272a;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #71717a;
    }

    /* BRAND */

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 28px;
    }

    .brand-icon {
        width: 43px;
        height: 43px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fafafa;
        color: #09090b;
        border-radius: 11px;
        font-size: 22px;
        font-weight: 800;
    }

    .brand-name {
        color: #fafafa;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: -0.4px;
    }

    .brand-subtitle {
        color: #71717a;
        font-size: 11px;
        margin-top: 4px;
    }

    .section-label {
        color: #71717a;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 20px 0 10px 0;
    }

    /* PAGE HEADER */

    .page-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
        margin-bottom: 26px;
    }

    .page-title {
        color: #fafafa;
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -1.3px;
        line-height: 1.3;
    }

    .page-description {
        color: #a1a1aa;
        font-size: 13px;
        margin-top: 8px;
        line-height: 1.8;
        max-width: 720px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #111113;
        border: 1px solid #27272a;
        color: #d4d4d8;
        padding: 9px 13px;
        border-radius: 8px;
        font-size: 11px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
    }

    /* METRIC CARDS */

    [data-testid="stMetric"] {
        background: #111113;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 18px 19px;
        min-height: 120px;
        transition: border-color 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: #52525b;
    }

    [data-testid="stMetricLabel"] {
        color: #a1a1aa !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        color: #fafafa !important;
        font-size: clamp(19px, 1.8vw, 27px) !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
        margin-top: 9px;
    }

    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
    }

    /* TABS */

    [data-testid="stTabs"] {
        margin-top: 12px;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 5px;
        border-bottom: 1px solid #27272a;
        background: transparent;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        height: 46px;
        padding: 0 15px;
        background: transparent;
        border-radius: 7px 7px 0 0;
        color: #a1a1aa;
        font-size: 12px;
        font-weight: 500;
        border-bottom: 2px solid transparent;
    }

    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: #fafafa;
        background: #18181b;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        color: #fafafa !important;
        border-bottom: 2px solid #818cf8 !important;
        background: transparent !important;
    }

    /* HEADINGS */

    h1, h2, h3, h4 {
        color: #fafafa !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }

    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    p, li {
        color: #d4d4d8;
    }

    [data-testid="stCaptionContainer"] {
        color: #a1a1aa !important;
        font-size: 12px;
    }

    /* CHARTS */

    [data-testid="stPlotlyChart"] {
        background: #111113;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 8px;
        overflow: hidden;
    }

    /* TABLES */

    [data-testid="stDataFrame"] {
        border: 1px solid #27272a;
        border-radius: 9px;
        overflow: hidden;
    }

    /* INPUTS */

    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        border-radius: 7px;
    }

    /* NOTICES */

    [data-testid="stAlert"] {
        background: #111113;
        border: 1px solid #27272a;
        border-radius: 9px;
    }

    /* DIVIDERS */

    hr {
        border-color: #27272a !important;
        margin: 22px 0;
    }

    /* FOOTER */

    .dashboard-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    border-top: 1px solid #27272a;
    padding-top: 20px;
    margin-top: 28px;
    color: #71717a;
    font-size: 11px;
    
    }
    
    .footer-brand {
    color: #a1a1aa;
    font-weight: 600;
    }
    
    .data-source {
    color: #71717a;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 400;
    line-height: 1.6;
    text-align: right;
    
    }
    
    @media (max-width: 600px) {
    .data-source {
        text-align: left;
        }
    }

    /* RESPONSIVE */

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.2rem 1rem 2rem 1rem;
        }

        .page-title {
            font-size: 24px;
        }

        [data-testid="stMetric"] {
            padding: 14px;
        }
    }

    
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PLOTLY THEME — COLORFUL CHARTS ON DARK BACKGROUND
# ============================================================

CHART_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#111113",
        plot_bgcolor="#111113",
        font=dict(
            family="Inter, sans-serif",
            color="#a1a1aa",
            size=12,
        ),
        title=dict(
            font=dict(
                family="Inter, sans-serif",
                size=15,
                color="#fafafa",
            ),
            x=0.02,
            xanchor="left",
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            tickfont=dict(size=10, color="#a1a1aa"),
            title_font=dict(size=11, color="#a1a1aa"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#27272a",
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=dict(size=10, color="#a1a1aa"),
            title_font=dict(size=11, color="#a1a1aa"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#d4d4d8"),
        ),
        margin=dict(l=25, r=20, t=55, b=30),
        hoverlabel=dict(
            bgcolor="#18181b",
            bordercolor="#3f3f46",
            font=dict(
                family="Inter, sans-serif",
                color="#fafafa",
                size=12,
            ),
        ),
        colorway=PALETTE,
    )
)

px.defaults.template = CHART_TEMPLATE
px.defaults.color_discrete_sequence = PALETTE


def style_chart(fig, height=380):
    """Apply consistent dark styling while preserving chart colors."""

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        autosize=True,
        paper_bgcolor="#111113",
        plot_bgcolor="#111113",
        font=dict(
            family="Inter, sans-serif",
            color="#a1a1aa",
        ),
        margin=dict(l=25, r=20, t=55, b=30),
    )

    return fig


def chart(fig, height=380, key=None):
    """Render a responsive Plotly chart."""

    style_chart(fig, height=height)

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displaylogo": False,
            "responsive": True,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
        key=key,
    )


# ============================================================
# DATA LOADING — ORIGINAL LOGIC PRESERVED
# ============================================================

@st.cache_data
def get_data() -> pd.DataFrame:
    return load_clean_data()


df = get_data()

if df.empty:
    st.error("The Superstore dataset is empty. Check your data source.")
    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">S</div>
            <div>
                <div class="brand-name">Superstore Analytics</div>
                <div class="brand-subtitle">Sales intelligence platform</div>
            </div>
        </div>

        <div class="section-label">Workspace</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Filters")
    st.caption("Refine the data shown across your dashboard.")

    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    date_range = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )

    st.markdown("---")

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

    st.markdown("---")

    st.markdown(
        """
        <div class="section-label">About</div>

        <div style="
            color:#a1a1aa;
            font-size:12px;
            line-height:1.8;
        ">
            Explore sales performance, profitability,
            customer behavior, geographic trends,
            and future revenue.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SUPERSTORE · ANALYTICS V1.0")


# ============================================================
# FILTER DATA
# ============================================================

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])

    # Include all orders on the selected ending date.
    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

else:

    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date) + pd.Timedelta(days=1)


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
# PAGE HEADER
# ============================================================


st.markdown(
    """
    <div class="page-header">
        <div class="page-heading">
            <div class="page-title">Sales Dashboard</div>
            <div class="page-description">
                Monitor business performance, discover customer insights,
                and explore trends across your retail business.
            </div>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
            <span>Analytics dashboard active</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# KPI CARDS
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


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# ANALYTICS TABS
# ============================================================

tab_trends, tab_products, tab_customers, tab_geo, tab_forecast = st.tabs(
    [
        "📈 Trends",
        "📦 Products",
        "👥 Customers",
        "🗺️ Geography",
        "🔮 Forecast",
    ]
)


# ============================================================
# TAB 1 — SALES TRENDS
# ============================================================

with tab_trends:

    st.markdown("### Sales & Profit Trends")
    st.caption(
        "Track monthly sales and profitability across the selected period."
    )

    ts = sa.yearly_monthly_trend(filtered)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ts["Year-Month"],
            y=ts["Sales"],
            name="Sales",
            mode="lines",
            line=dict(
                color="#818cf8",
                width=3,
            ),
            fill="tozeroy",
            fillcolor="rgba(129,140,248,0.12)",
            hovertemplate=(
                "<b>Sales</b><br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ts["Year-Month"],
            y=ts["Profit"],
            name="Profit",
            mode="lines",
            line=dict(
                color="#22c55e",
                width=2.5,
            ),
            hovertemplate=(
                "<b>Profit</b><br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="$",
        yaxis_tickformat="~s",
    )

    chart(fig, height=420, key="sales_profit_trend")

    st.markdown("---")

    st.markdown("### Discount vs. Profitability")
    st.caption(
        "Explore the relationship between discount levels and profit margins."
    )

    disc = sa.discount_profit_relationship(filtered)

    fig2 = px.bar(
        disc,
        x="Discount Bucket",
        y="Avg_Profit_Margin",
        color="Avg_Profit_Margin",
        color_continuous_scale=[
            "#ef4444",
            "#f97316",
            "#f59e0b",
            "#84cc16",
            "#22c55e",
        ],
        labels={
            "Discount Bucket": "Discount range",
            "Avg_Profit_Margin": "Average profit margin",
        },
    )

    fig2.update_layout(
        coloraxis_showscale=False,
        yaxis_tickformat=".0%",
    )

    fig2.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "Discount: %{x}<br>"
            "Average margin: %{y:.1%}"
            "<extra></extra>"
        ),
    )

    chart(fig2, height=360, key="discount_profit")


# ============================================================
# TAB 2 — PRODUCTS
# ============================================================

with tab_products:

    st.markdown("### Product Performance")
    st.caption(
        "Understand how product categories contribute to sales and profit."
    )

    cat = sa.by_category(filtered)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("#### Sales by Category")

        fig3 = px.pie(
            cat,
            names="Category",
            values="Sales",
            hole=0.65,
            color_discrete_sequence=[
                "#818cf8",
                "#06b6d4",
                "#f59e0b",
                "#22c55e",
                "#ec4899",
            ],
        )

        fig3.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(
                    color="#111113",
                    width=3,
                )
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Sales: $%{value:,.2f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )

        chart(fig3, height=350, key="sales_by_category")

    with c2:

        st.markdown("#### Profit by Category")

        fig4 = px.pie(
            cat,
            names="Category",
            values="Profit",
            hole=0.65,
            color_discrete_sequence=[
                "#22c55e",
                "#818cf8",
                "#f59e0b",
                "#06b6d4",
                "#ec4899",
            ],
        )

        fig4.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(
                    color="#111113",
                    width=3,
                )
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Profit: $%{value:,.2f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )

        chart(fig4, height=350, key="profit_by_category")

    st.markdown("---")

    st.markdown("### Sales & Profit by Sub-Category")
    st.caption(
        "Compare sales and profit across individual product sub-categories."
    )

    subcat = sa.by_subcategory(filtered)

    fig5 = go.Figure()

    fig5.add_trace(
        go.Bar(
            x=subcat["Sub-Category"],
            y=subcat["Sales"],
            name="Sales",
            marker_color="#818cf8",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Sales: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig5.add_trace(
        go.Bar(
            x=subcat["Sub-Category"],
            y=subcat["Profit"],
            name="Profit",
            marker_color="#22c55e",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Profit: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig5.update_layout(
        barmode="group",
        height=440,
        xaxis_tickangle=-35,
        yaxis_tickprefix="$",
        yaxis_tickformat="~s",
    )

    chart(fig5, height=440, key="subcategory_performance")

    st.markdown("---")

    st.markdown("### Top 10 Products by Sales")
    st.caption("Products ranked by sales using your existing analysis module.")

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

    st.markdown("### Customer Intelligence")

    st.caption(
        "RFM analysis explores customer purchasing behavior using "
        "Recency, Frequency, and Monetary value."
    )

    rfm = cs.compute_rfm(filtered)
    seg_summary = cs.segment_summary(rfm)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("#### Customers by Segment")

        fig6 = px.bar(
            seg_summary,
            x="Segment",
            y="Customers",
            color="Segment",
            color_discrete_sequence=PALETTE,
            labels={
                "Segment": "Customer segment",
                "Customers": "Number of customers",
            },
        )

        fig6.update_layout(
            showlegend=False,
            xaxis_tickangle=-25,
        )

        fig6.update_traces(
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Customers: %{y:,}"
                "<extra></extra>"
            ),
        )

        chart(fig6, height=390, key="customer_segments")

    with c2:

        st.markdown("#### Frequency vs. Monetary Value")

        fig7 = px.scatter(
            rfm,
            x="Frequency",
            y="Monetary",
            color="Segment",
            size="Recency",
            hover_data=["Customer_Name"],
            color_discrete_sequence=PALETTE,
            labels={
                "Frequency": "Purchase frequency",
                "Monetary": "Monetary value ($)",
                "Recency": "Recency",
            },
        )

        fig7.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(
                    width=0.5,
                    color="#111113",
                ),
            ),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Frequency: %{x}<br>"
                "Monetary value: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )

        fig7.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat="~s",
        )

        chart(fig7, height=390, key="customer_scatter")

    st.markdown("---")

    st.markdown("### Customer Segment Summary")

    st.dataframe(
        seg_summary,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# TAB 4 — GEOGRAPHY
# ============================================================

with tab_geo:

    st.markdown("### Geographic Performance")

    st.caption(
        "Explore differences in sales and profitability across US states."
    )

    metric = st.radio(
        "Map metric",
        ["Sales", "Profit"],
        horizontal=True,
    )

    geo = ga.state_summary(filtered)

    if metric == "Profit":

        map_colors = [
            "#7f1d1d",
            "#ef4444",
            "#f59e0b",
            "#84cc16",
            "#22c55e",
        ]

    else:

        map_colors = [
            "#172554",
            "#1d4ed8",
            "#3b82f6",
            "#06b6d4",
            "#a5f3fc",
        ]

    fig8 = px.choropleth(
        geo,
        locations="State Code",
        locationmode="USA-states",
        color=metric,
        scope="usa",
        color_continuous_scale=map_colors,
        hover_name="State",
        labels={
            "State Code": "State",
            metric: metric,
        },
    )

    fig8.update_layout(
        height=530,
        geo=dict(
            bgcolor="#111113",
            lakecolor="#111113",
            showlakes=True,
            subunitcolor="#27272a",
            countrycolor="#27272a",
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(
                color="#a1a1aa",
                size=10,
            ),
            title=dict(
                text=metric,
                font=dict(color="#d4d4d8"),
            ),
            outlinecolor="#27272a",
        ),
    )

    chart(fig8, height=530, key="state_map")

    st.markdown("---")

    st.markdown("### State Profitability Rankings")

    top_bottom = ga.top_bottom_states(filtered, n=5)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div style="
                color:#22c55e;
                font-size:14px;
                font-weight:600;
                margin-bottom:10px;
            ">
                ↑ Top 5 States by Profit
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(
            top_bottom["top_profit"],
            width="stretch",
            hide_index=True,
        )

    with c2:

        st.markdown(
            f"""
            <div style="
                color:#f87171;
                font-size:14px;
                font-weight:600;
                margin-bottom:10px;
            ">
                ↓ Bottom 5 States by Profit
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(
            top_bottom["bottom_profit"],
            width="stretch",
            hide_index=True,
        )


# ============================================================
# TAB 5 — SALES FORECAST
# ============================================================

with tab_forecast:

    st.markdown("### Sales Forecast")

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

        st.markdown(
            f"""
            <div style="
                margin-top:26px;
                padding:12px 15px;
                background:#111113;
                border:1px solid #27272a;
                border-radius:9px;
                font-size:12px;
                color:#a1a1aa;
            ">
                Forecast horizon:
                <strong style="color:#818cf8">{horizon} months</strong>
                &nbsp; · &nbsp;
                Model:
                <strong style="color:#06b6d4">Holt-Winters</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Preserve the original behavior: use full history.
    forecast_df = fc.forecast_sales(
        df,
        periods=horizon,
    )

    fig9 = px.line(
        forecast_df,
        x="Date",
        y="Sales",
        color="Type",
        color_discrete_map={
            "Actual": "#06b6d4",
            "Forecast": "#a78bfa",
        },
        labels={
            "Date": "Date",
            "Sales": "Sales ($)",
            "Type": "Series",
        },
    )

    fig9.update_traces(
        line=dict(width=2.8),
    )

    # Distinguish forecast from actual observations.
    for trace in fig9.data:

        if trace.name == "Actual":
            trace.update(
                line=dict(
                    color="#06b6d4",
                    width=2.8,
                )
            )

        elif trace.name == "Forecast":
            trace.update(
                line=dict(
                    color="#a78bfa",
                    width=3,
                    dash="dash",
                )
            )

    fig9.update_layout(
        height=480,
        hovermode="x unified",
        yaxis_tickprefix="$",
        yaxis_tickformat="~s",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    chart(fig9, height=480, key="sales_forecast")

    st.markdown("---")

    st.markdown("### Forecast Data")

    st.dataframe(
        forecast_df,
        width="stretch",
        hide_index=True,
    )

    st.info(
        "The forecast uses the full order history, regardless of the sidebar "
        "filters, to preserve the historical time series. Predictions are "
        "estimates and are not guaranteed future results."
    )


# ============================================================
# FOOTER
# ============================================================

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="dashboard-footer">
        <div>
            <span class="footer-brand">Superstore Analytics</span>
            &nbsp;·&nbsp;
            Sales Intelligence Platform
        </div>
        <div class="data-source">
            Data source: Sample Superstore dataset
        </div>
    </div>
    """,
    unsafe_allow_html=True,
) 