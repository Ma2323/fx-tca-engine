import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tca_engine import FXTCAEngine

st.set_page_config(page_title="FX Treasury TCA Dashboard", layout="wide")

st.title("FX Transaction Cost Analysis (TCA) & Execution Quality Engine")
st.markdown("Automated Treasury trade execution reporting, liquidity provider benchmarking, and slippage attribution.")

@st.cache_resource
def get_engine():
    engine = FXTCAEngine()
    engine.load_csv_to_sql()
    return engine

engine = get_engine()
df_slippage = engine.calculate_slippage_analysis()
df_counterparties = engine.calculate_counterparty_metrics()

# Sidebar Filters
st.sidebar.header("Execution Filters")
selected_pairs = st.sidebar.multiselect(
    "Currency Pair", 
    options=df_slippage['currency_pair'].unique(), 
    default=df_slippage['currency_pair'].unique()
)
selected_cps = st.sidebar.multiselect(
    "Counterparties", 
    options=df_slippage['counterparty'].unique(), 
    default=df_slippage['counterparty'].unique()
)

filtered_df = df_slippage[
    (df_slippage['currency_pair'].isin(selected_pairs)) & 
    (df_slippage['counterparty'].isin(selected_cps))
]

# Top-level KPI metrics
total_trades = len(filtered_df)
total_volume = filtered_df['volume'].sum() / 1e6
avg_slippage = filtered_df['slippage_bps'].mean()
vw_slippage = (filtered_df['slippage_bps'] * filtered_df['volume']).sum() / filtered_df['volume'].sum() if total_volume > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Executed Trades", f"{total_trades:,}")
col2.metric("Total Executed Volume", f"${total_volume:,.2f} M")
col3.metric("Avg Slippage", f"{avg_slippage:.2f} bps")
col4.metric("Volume-Weighted Slippage", f"{vw_slippage:.2f} bps")

st.markdown("---")

# Layout: 2 Columns of Charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Counterparty Fill Rate & Latency")
    fig_fill = px.bar(
        df_counterparties, 
        x='counterparty', 
        y='fill_rate_pct', 
        color='avg_latency_ms',
        title="Fill Rate (%) vs Average Latency (ms)",
        labels={'fill_rate_pct': 'Fill Rate (%)', 'avg_latency_ms': 'Latency (ms)'},
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_fill, use_container_width=True)

with chart_col2:
    st.subheader("Slippage Distribution (Basis Points)")
    fig_hist = px.histogram(
        filtered_df, 
        x='slippage_bps', 
        color='currency_pair', 
        nbins=40,
        marginal='box',
        title="Execution Slippage Distribution by Pair",
        labels={'slippage_bps': 'Slippage (bps)'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# Performance Breakdown by Counterparty
st.subheader("Counterparty Execution Quality Breakdown")
summary_table = filtered_df.groupby('counterparty').agg(
    Trades=('trade_id', 'count'),
    Total_Vol_M=('volume', lambda x: f"${x.sum()/1e6:.2f}M"),
    Mean_Slippage_bps=('slippage_bps', 'mean'),
    Std_Dev_bps=('slippage_bps', 'std'),
    Avg_Latency_ms=('latency_ms', 'mean')
).reset_index()

st.dataframe(summary_table, width="stretch")