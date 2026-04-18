"""
Malaria Burden Dashboard - Funding Priority Analysis
Designed for Funding Agencies: Concise, Actionable, Data-Driven
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config - optimized for executive dashboard
st.set_page_config(
    page_title="Malaria Funding Priority Dashboard",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aggressive styling for maximum impact
st.markdown("""
<style>
    body { font-family: 'Segoe UI', sans-serif; }
    .urgent-box {
        background: linear-gradient(135deg, #ff4757 0%, #ff6348 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
    }
    .urgent-title { font-size: 28px; font-weight: 900; margin: 0; }
    .urgent-subtitle { font-size: 16px; margin-top: 8px; opacity: 0.95; }
    .funding-title { font-size: 32px; font-weight: 900; color: #1a1a1a; margin: 0; }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .stat-number { font-size: 24px; font-weight: 900; }
    .stat-label { font-size: 11px; opacity: 0.85; margin-top: 5px; }
    .priority-1 { background: linear-gradient(135deg, #ff4757 0%, #ff6348 100%); }
    .priority-2 { background: linear-gradient(135deg, #ff9f43 0%, #ffb347 100%); }
    .priority-3 { background: linear-gradient(135deg, #ffd93d 0%, #ffed4e 100%); color: #333; }
    .recommendation-box {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
    }
    .separator { margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

# Load data - Synthetic malaria surveillance data
@st.cache_data
def load_data():
    """Generate synthetic CLMV malaria surveillance data (2015-2025)"""
    import numpy as np
    
    np.random.seed(42)
    countries = ['Cambodia', 'Laos', 'Myanmar', 'Vietnam']
    regions = {
        'Cambodia': ['Phnom Penh', 'Siem Reap', 'Battambang'],
        'Laos': ['Vientiane', 'Luang Prabang', 'Savannakhet'],
        'Myanmar': ['Yangon', 'Mandalay', 'Shan'],
        'Vietnam': ['Hanoi', 'Ho Chi Minh', 'Da Nang']
    }
    
    data = []
    for country in countries:
        for year in range(2015, 2026):
            for month in range(1, 13):
                for region in regions[country]:
                    base_cases = np.random.randint(100, 800)
                    # Trend: declining over time
                    trend_factor = 1 - ((year - 2015) * 0.03)
                    cases = int(base_cases * trend_factor * np.random.uniform(0.8, 1.2))
                    deaths = int(cases * np.random.uniform(0.01, 0.05))
                    
                    data.append({
                        'country': country,
                        'region': region,
                        'year': year,
                        'month': month,
                        'confirmed_cases': max(0, cases),
                        'deaths': max(0, deaths),
                        'severe_cases': int(cases * 0.15),
                        'population': np.random.randint(800000, 5000000),
                        'pf_cases': int(cases * 0.6),
                        'pv_cases': int(cases * 0.4)
                    })
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    return df

df = load_data()



# ============================================================
# HEADER
# ============================================================
st.markdown('<p class="funding-title">🦟 MALARIA FUNDING PRIORITY DASHBOARD</p>', unsafe_allow_html=True)
st.markdown("**CLMV Region | 2015-2025** | Synthetic Surveillance System")

# ============================================================
# CALCULATE PRIORITY SCORES UPFRONT
# ============================================================
clmv_countries = ['Cambodia', 'Laos', 'Myanmar', 'Vietnam']
priority_df = df[df['country'].isin(clmv_countries)].groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'population': 'mean'
}).reset_index()

priority_df['case_rate'] = (priority_df['confirmed_cases'] / priority_df['population'] * 1000).round(2)
priority_df['cfr'] = (priority_df['deaths'] / priority_df['confirmed_cases'] * 100).round(2)

# Calculate epidemiologically-sound priority score
# Components: Mortality Risk (CFR) + Disease Burden (population-adjusted rate) + Absolute Deaths
priority_df['cfr_normalized'] = priority_df['cfr'] / priority_df['cfr'].max() * 40  # Severity
priority_df['rate_normalized'] = priority_df['case_rate'] / priority_df['case_rate'].max() * 35  # Burden
priority_df['deaths_normalized'] = priority_df['deaths'] / priority_df['deaths'].max() * 25  # Scale

priority_df['priority_score'] = (
    priority_df['cfr_normalized'] + 
    priority_df['rate_normalized'] + 
    priority_df['deaths_normalized']
).round(1)

priority_df = priority_df.sort_values('priority_score', ascending=False).reset_index(drop=True)

# Get top priority country
top_country = priority_df.iloc[0]
total_cases = priority_df['confirmed_cases'].sum()
total_deaths = priority_df['deaths'].sum()

# ============================================================
# PROBLEM STATEMENT (AT A GLANCE) - Funder Focus
# ============================================================
top_country_name = top_country['country']
top_cfr = top_country['cfr']
top_rate = top_country['case_rate']
alert_msg = f"{top_country_name}: {int(top_country['deaths']):,} deaths annually | Highest mortality risk per case ({top_cfr:.1f}%) | Most urgent funding need"
st.markdown(f'<div class="urgent-box"><p class="urgent-title">⚠️ FUNDING RECOMMENDATION</p><p class="urgent-subtitle">{alert_msg}</p></div>', unsafe_allow_html=True)

# ============================================================
# EXECUTIVE METRICS - EPIDEMIOLOGICAL FOCUS
# ============================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{int(total_cases):,}</div><div class="stat-label">TOTAL CASES</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{int(total_deaths):,}</div><div class="stat-label">ANNUAL DEATHS</div></div>', unsafe_allow_html=True)
with col3:
    cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    st.markdown(f'<div class="stat-box"><div class="stat-number">{cfr:.1f}%</div><div class="stat-label">MORTALITY RATE</div></div>', unsafe_allow_html=True)
with col4:
    overall_rate = (total_cases / priority_df['population'].sum() * 1000)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{overall_rate:.1f}</div><div class="stat-label">CASES/1K PEOPLE</div></div>', unsafe_allow_html=True)

# ============================================================
# TOP PRIORITY COUNTRY SPOTLIGHT
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

col_spotlight, col_allocation = st.columns([1.3, 0.7])

with col_spotlight:
    st.markdown(f"### 🔴 WHERE YOUR FUNDING MATTERS MOST: {top_country_name}")
    
    # Priority score comparison across all countries
    fig_priority_comparison = px.bar(
        priority_df.sort_values('priority_score', ascending=True),
        y='country',
        x='priority_score',
        orientation='h',
        text='priority_score',
        color='priority_score',
        color_continuous_scale=['#95a5a6', '#ff9f43', '#ff6348', '#ff4757'],
        title='Priority Score Across CLMV Countries',
        labels={'priority_score': 'Priority Score', 'country': 'Country'}
    )
    fig_priority_comparison.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont=dict(size=14, color='#1a1a1a'))
    fig_priority_comparison.update_layout(
        height=280,
        showlegend=False,
        xaxis_title='Priority Score',
        yaxis_title='',
        plot_bgcolor='rgba(240,240,240,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=100, r=50, t=40, b=40)
    )
    st.plotly_chart(fig_priority_comparison, use_container_width=True)

with col_allocation:
    st.markdown("### 💰 RECOMMENDED ALLOCATION")
    
    summary_df = priority_df[['country', 'priority_score']].copy()
    total_score = summary_df['priority_score'].sum()
    summary_df['funding_pct'] = (summary_df['priority_score'] / total_score * 100).round(1)
    summary_df = summary_df.sort_values('funding_pct', ascending=False)
    
    # Clear allocation table - simplified for reliability
    alloc_display = summary_df[['country', 'funding_pct']].copy()
    alloc_display.columns = ['Country', 'Allocation %']
    
    st.dataframe(
        alloc_display.style.format({'Allocation %': '{:.1f}%'}),
        use_container_width=True,
        hide_index=True,
        height=180
    )
    
    top_funding = summary_df.iloc[0]['funding_pct']
    st.markdown(f'<div class="recommendation-box">👉 {top_country_name}: {top_funding:.1f}%<br/>Priority: Highest</div>', unsafe_allow_html=True)

# ============================================================
# COUNTRY RANKINGS (SIMPLE TABLE)
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("### 🔬 EPIDEMIOLOGICAL PROFILE - All Countries")

ranking_table = priority_df[['country', 'confirmed_cases', 'deaths', 'cfr', 'case_rate', 'priority_score']].copy()
ranking_table.columns = ['Country', 'Cases', 'Deaths', 'CFR %', 'Rate/1K Pop', 'Priority Score']
ranking_table['Cases'] = ranking_table['Cases'].apply(lambda x: f"{int(x):,}")
ranking_table['Deaths'] = ranking_table['Deaths'].apply(lambda x: f"{int(x):,}")
ranking_table['CFR %'] = ranking_table['CFR %'].apply(lambda x: f"{x:.2f}%")
ranking_table['Rate/1K Pop'] = ranking_table['Rate/1K Pop'].apply(lambda x: f"{x:.1f}")

st.dataframe(
    ranking_table.style.format({'Priority Score': '{:.1f}'}),
    use_container_width=True,
    hide_index=True,
    height=200
)

st.success("✓ **Funding Allocation Based On**: 40% Mortality Risk (CFR) + 35% Population Disease Burden + 25% Total Deaths | Countries with higher death rates or more deaths get more funding")


# ============================================================
# TREND CONFIRMATION
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("### 📈 Is the Problem Getting Worse?")

country_year_df = df.groupby(['year', 'country']).agg({
    'confirmed_cases': 'sum'
}).reset_index().sort_values('year')

# Highlight Vietnam with bold color, others more subtle
color_map = {
    'Vietnam': '#ff4757',  # Bold red - focal point
    'Myanmar': '#ffa502',   # Orange
    'Cambodia': '#95a5a6',  # Gray
    'Laos': '#95a5a6'       # Gray
}

fig_trend = px.line(
    country_year_df,
    x='year',
    y='confirmed_cases',
    color='country',
    markers=True,
    title='10-Year Malaria Cases Trend - Focus: Vietnam',
    labels={'confirmed_cases': 'Annual Cases', 'year': 'Year', 'country': 'Country'},
    color_discrete_map=color_map
)

# Make Vietnam line thicker
for trace in fig_trend.data:
    if trace.name == 'Vietnam':
        trace.line.width = 4
        trace.marker.size = 10
    else:
        trace.line.width = 2
        trace.marker.size = 6

fig_trend.update_layout(
    height=400,  # Increased from 220
    hovermode='x unified',
    showlegend=True,
    plot_bgcolor='rgba(240,240,240,0.5)',
    yaxis_title='Annual Cases',
    xaxis_title='Year',
    font=dict(size=12)
)

st.plotly_chart(fig_trend, use_container_width=True)

# Context below chart
col_cases, col_info = st.columns([2, 1])
with col_cases:
    vietnam_trend = country_year_df[country_year_df['country'] == 'Vietnam'].sort_values('year')
    if len(vietnam_trend) > 1:
        vietnam_start = vietnam_trend.iloc[0]['confirmed_cases']
        vietnam_end = vietnam_trend.iloc[-1]['confirmed_cases']
        vietnam_change = ((vietnam_end - vietnam_start) / vietnam_start * 100) if vietnam_start > 0 else 0
        st.write(f"**Vietnam Trajectory**: {int(vietnam_start):,} cases (2015) → {int(vietnam_end):,} cases (2025) | Change: {vietnam_change:+.1f}%")

with col_info:
    st.markdown("**Interpretation**")
    st.info("📊 Compare Vietnam's burden against other countries to understand relative urgency")

st.markdown("---")
st.markdown("💡 **How We Prioritize Your Funding**: We look at three things: (1) **Mortality Risk** (40%) - How many people die from malaria in each country? This tells us where healthcare is weakest. (2) **Population Impact** (35%) - How many people in each country get malaria? This shows scale of the problem. (3) **Total Deaths** (25%) - Raw count of lives at stake. Countries with deadlier malaria, worse healthcare systems, or more deaths get prioritized first. | **Note**: Using Synthetic Surveillance Data (2015-2025) | Last Updated: 2026")
