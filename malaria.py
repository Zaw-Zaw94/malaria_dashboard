"""
Malaria Burden Dashboard - Funding Priority Analysis
Designed for Funding Agencies: Concise, Actionable, Data-Driven
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Malaria Funding Priority Dashboard",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .priority-high { background-color: #ff6b6b; color: white; padding: 3px 8px; border-radius: 4px; }
    .priority-medium { background-color: #ffa94d; color: white; padding: 3px 8px; border-radius: 4px; }
    .priority-low { background-color: #51cf66; color: white; padding: 3px 8px; border-radius: 4px; }
    .funding-title { font-size: 24px; font-weight: bold; color: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("burden_cleaned.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    numeric_cols = ['confirmed_cases', 'pf_cases', 'pv_cases', 'severe_cases', 'deaths', 
                    'border_crossings', 'migrants_in', 'migrants_out', 'population']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# Sidebar - Minimal filters
with st.sidebar:
    st.markdown("### 📊 Dashboard Filters")
    selected_year = st.selectbox("View Year", options=['All'] + sorted([int(y) for y in df['year'].unique()]))
    st.markdown("---")
    st.caption("💡 Use filters to explore specific data. Default: All years (2015-2025)")

# Filter data
def filter_data():
    mask = pd.Series([True] * len(df))
    if selected_year != 'All':
        mask &= (df['year'] == selected_year)
    return df[mask]

filtered_df = filter_data()

# ============================================================
# HEADER & EXECUTIVE SUMMARY
# ============================================================
st.markdown('<p class="funding-title">🦟 MALARIA FUNDING PRIORITY DASHBOARD</p>', unsafe_allow_html=True)
st.caption(f"Last Updated: {datetime.now().strftime('%B %d, %Y')} | Region: CLMV (Cambodia, Laos, Myanmar, Vietnam)")
st.markdown("---")

# Executive Summary - Key Metrics
st.subheader("📋 Executive Summary: Regional Burden")

exec_summary = filtered_df.groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'population': 'mean'
}).reset_index()

total_cases = exec_summary['confirmed_cases'].sum()
total_deaths = exec_summary['deaths'].sum()
avg_cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
affected_countries = len(exec_summary)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 Total Cases", f"{int(total_cases):,}")
col2.metric("💀 Total Deaths", f"{int(total_deaths):,}")
col3.metric("⚠️ Case Fatality Rate", f"{avg_cfr:.2f}%")
col4.metric("🗺️ Countries Affected", f"{affected_countries}")

st.markdown("---")

# ============================================================
# FUNDING PRIORITY RANKING - THE KEY DECISION
# ============================================================
st.subheader("🎯 FUNDING PRIORITY RANKING (Your Decision)")

clmv_countries = ['Cambodia', 'Laos', 'Myanmar', 'Vietnam']
priority_df = df[df['country'].isin(clmv_countries)].groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'population': 'mean'
}).reset_index()

# Calculate metrics
priority_df['case_rate'] = (priority_df['confirmed_cases'] / priority_df['population'] * 1000).round(2)
priority_df['mortality_rate'] = (priority_df['deaths'] / priority_df['population'] * 100000).round(1)
priority_df['cfr'] = (priority_df['deaths'] / priority_df['confirmed_cases'] * 100).round(2)

# Calculate priority score (weighted)
priority_df['priority_score'] = (
    (priority_df['confirmed_cases'] / priority_df['confirmed_cases'].max() * 35) +
    (priority_df['deaths'] / priority_df['deaths'].max() * 35) +
    (priority_df['case_rate'] / priority_df['case_rate'].max() * 30)
).round(1)

priority_df = priority_df.sort_values('priority_score', ascending=False).reset_index(drop=True)
priority_df['rank'] = range(1, len(priority_df) + 1)

# Visualization: Priority Ranking Bar Chart
fig_priority = px.bar(
    priority_df,
    x='country',
    y='priority_score',
    text='priority_score',
    color='priority_score',
    color_continuous_scale=['#51cf66', '#ffa94d', '#ff6b6b'],
    labels={'priority_score': 'Priority Score', 'country': 'Country'},
    hover_data={'priority_score': ':.1f', 'confirmed_cases': ',.0f', 'deaths': ',.0f'},
    title="Priority Score: Higher = More Urgent Funding Need"
)
fig_priority.update_layout(height=350, showlegend=False)
fig_priority.add_annotation(
    text="Scale: 0-100 | Based on: Case Volume (35%) + Deaths (35%) + Case Rate (30%)",
    xref="paper", yref="paper", x=0.5, y=-0.15, showarrow=False, font=dict(size=10, color="gray")
)
st.plotly_chart(fig_priority, use_container_width=True)

# Detailed Comparison Table
st.markdown("### Detailed Country Comparison")
comparison_table = priority_df[['rank', 'country', 'confirmed_cases', 'deaths', 'case_rate', 'cfr', 'priority_score']].copy()
comparison_table.columns = ['Rank', 'Country', 'Total Cases', 'Total Deaths', 'Case Rate\n(per 1000)', 'Fatality Rate\n(%)', 'Priority\nScore']
comparison_table['Total Cases'] = comparison_table['Total Cases'].apply(lambda x: f"{int(x):,}")
comparison_table['Total Deaths'] = comparison_table['Total Deaths'].apply(lambda x: f"{int(x):,}")

# Format for display
st.dataframe(
    comparison_table.style.format({'Case Rate\n(per 1000)': '{:.2f}', 'Fatality Rate\n(%)': '{:.2f}', 'Priority\nScore': '{:.1f}'}),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ============================================================
# TREND ANALYSIS - IS IT IMPROVING?
# ============================================================
st.subheader("📈 Trend Analysis: 10-Year Trajectory (2015-2025)")

country_year_df = df.groupby(['year', 'country']).agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum'
}).reset_index().sort_values('year')

# Calculate trend direction
trend_calc = country_year_df.copy()
trend_calc['2015_cases'] = trend_calc.groupby('country')['confirmed_cases'].transform('first')
trend_calc['2025_cases'] = trend_calc.groupby('country')['confirmed_cases'].transform('last')
trend_calc['trend_pct'] = ((trend_calc['2025_cases'] - trend_calc['2015_cases']) / trend_calc['2015_cases'] * 100).round(1)

col_trend_cases, col_trend_deaths = st.columns(2)

# Cases Trend
with col_trend_cases:
    fig_cases = px.line(
        country_year_df,
        x='year',
        y='confirmed_cases',
        color='country',
        markers=True,
        title="Cases Trend (2015-2025)",
        labels={'confirmed_cases': 'Cases', 'year': 'Year', 'country': 'Country'},
        line_shape='linear'
    )
    fig_cases.update_layout(height=350, hovermode='x unified', showlegend=True)
    st.plotly_chart(fig_cases, use_container_width=True)

# Deaths Trend
with col_trend_deaths:
    fig_deaths = px.line(
        country_year_df,
        x='year',
        y='deaths',
        color='country',
        markers=True,
        title="Deaths Trend (2015-2025)",
        labels={'deaths': 'Deaths', 'year': 'Year', 'country': 'Country'},
        line_shape='linear'
    )
    fig_deaths.update_layout(height=350, hovermode='x unified', showlegend=True)
    st.plotly_chart(fig_deaths, use_container_width=True)

st.markdown("---")

# ============================================================
# TIME SERIES - CURRENT STATUS
# ============================================================
st.subheader("⏱️ Recent Trend: Monthly Cases & Deaths Over Time")

agg_df = filtered_df.groupby(['year', 'month']).agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum'
}).reset_index()

agg_df['period'] = agg_df['year'].astype(str) + '-' + agg_df['month'].astype(str).str.zfill(2)
agg_df = agg_df.sort_values(['year', 'month'])

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=agg_df['period'], 
    y=agg_df['confirmed_cases'], 
    name="Cases", 
    line=dict(color='#1f77b4', width=2),
    yaxis='y1',
    hovertemplate='Period: %{x}<br>Cases: %{y:,}<extra></extra>'
))
fig_ts.add_trace(go.Scatter(
    x=agg_df['period'], 
    y=agg_df['deaths'], 
    name="Deaths", 
    line=dict(color='#d62728', width=2),
    yaxis='y2',
    hovertemplate='Period: %{x}<br>Deaths: %{y:,}<extra></extra>'
))

fig_ts.update_layout(
    title="Cases & Deaths Timeline",
    xaxis_title="Month",
    yaxis=dict(title="Cases", titlefont=dict(color='#1f77b4'), tickfont=dict(color='#1f77b4')),
    yaxis2=dict(title="Deaths", titlefont=dict(color='#d62728'), tickfont=dict(color='#d62728'), anchor="x", overlaying="y1"),
    hovermode='x unified',
    height=350,
    xaxis=dict(tickangle=-45)
)
st.plotly_chart(fig_ts, use_container_width=True)

st.markdown("---")

# ============================================================
# FUNDING ALLOCATION RECOMMENDATION
# ============================================================
st.subheader("💰 FUNDING ALLOCATION RECOMMENDATION")

summary_df = priority_df[['country', 'priority_score']].copy()
total_score = summary_df['priority_score'].sum()
summary_df['funding_pct'] = (summary_df['priority_score'] / total_score * 100).round(1)
summary_df = summary_df.sort_values('funding_pct', ascending=False)

fig_alloc = px.bar(
    summary_df,
    x='country',
    y='funding_pct',
    text='funding_pct',
    color='funding_pct',
    color_continuous_scale='Reds',
    labels={'funding_pct': 'Recommended Allocation (%)', 'country': 'Country'},
    title="Recommended Funding Distribution by Country"
)
fig_alloc.update_layout(height=350, showlegend=False)
st.plotly_chart(fig_alloc, use_container_width=True)

# Final Recommendation Table
st.markdown("### Funding Recommendation Summary")
rec_table = summary_df[['country', 'funding_pct', 'priority_score']].copy()
rec_table.columns = ['Country', 'Recommended Allocation (%)', 'Priority Score']

st.dataframe(
    rec_table.style.format({'Recommended Allocation (%)': '{:.1f}%', 'Priority Score': '{:.1f}'}),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ============================================================
# FOOTER & METHODOLOGY
# ============================================================
st.subheader("📌 Methodology & Data Notes")

col_method1, col_method2 = st.columns(2)

with col_method1:
    st.markdown("""
    **Priority Scoring Formula:**
    - Case Volume: 35% (absolute burden)
    - Deaths: 35% (severity)
    - Case Rate: 30% (population impact)
    
    **Data Quality:**
    - Time Period: 2015-2025 (11 years)
    - Countries: 4 CLMV nations
    - Records: 44,778 surveillance entries
    """)

with col_method2:
    st.markdown("""
    **Key Metrics:**
    - Confirmed Cases: Laboratory-verified
    - Deaths: Malaria-attributed mortality
    - Case Rate: Cases per 1000 population
    - CFR: Case Fatality Rate (%)
    
    **Source:** Malaria Surveillance System
    **Dashboard Purpose:** Aid resource allocation decisions
    """)

st.markdown("---")
st.caption("🔒 Confidential | For Funding Agency Use Only | Data Source: Regional Malaria Surveillance System")
