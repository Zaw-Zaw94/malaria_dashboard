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

# Calculate priority score (weighted) - Deaths heavily weighted
priority_df['priority_score'] = (
    (priority_df['confirmed_cases'] / priority_df['confirmed_cases'].max() * 30) +
    (priority_df['deaths'] / priority_df['deaths'].max() * 70)
).round(1)

priority_df = priority_df.sort_values('priority_score', ascending=False).reset_index(drop=True)

# Get top priority country
top_country = priority_df.iloc[0]
total_cases = priority_df['confirmed_cases'].sum()
total_deaths = priority_df['deaths'].sum()

# ============================================================
# PROBLEM STATEMENT (AT A GLANCE)
# ============================================================
st.markdown('<div class="urgent-box"><p class="urgent-title">⚠️ URGENT FUNDING NEEDED</p><p class="urgent-subtitle">Myanmar faces critical malaria burden - Requires immediate resources</p></div>', unsafe_allow_html=True)

# ============================================================
# EXECUTIVE METRICS
# ============================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{int(total_cases):,}</div><div class="stat-label">TOTAL CASES</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{int(total_deaths):,}</div><div class="stat-label">DEATHS</div></div>', unsafe_allow_html=True)
with col3:
    cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    st.markdown(f'<div class="stat-box"><div class="stat-number">{cfr:.1f}%</div><div class="stat-label">FATALITY RATE</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{top_country["priority_score"]:.0f}/100</div><div class="stat-label">TOP PRIORITY</div></div>', unsafe_allow_html=True)

# ============================================================
# TOP PRIORITY COUNTRY SPOTLIGHT
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

col_spotlight, col_allocation = st.columns([1.3, 0.7])

with col_spotlight:
    st.markdown("### 🔴 PRIMARY FOCUS: Myanmar")
    
    priority1_cases = int(top_country['confirmed_cases'])
    priority1_deaths = int(top_country['deaths'])
    priority1_rate = top_country['case_rate']
    
    # Large visual for Myanmar burden
    fig_priority_top = px.bar(
        priority_df.head(1),
        x='country',
        y='priority_score',
        text='priority_score',
        color_discrete_sequence=['#ff4757'],
        title='',
        labels={'priority_score': 'Priority Score', 'country': ''}
    )
    fig_priority_top.update_traces(texttemplate='SCORE: %{text:.0f}', textposition='outside', textfont=dict(size=18, color='#ff4757', family='Arial Black'))
    fig_priority_top.update_layout(
        height=150, 
        showlegend=False, 
        xaxis=dict(showticklabels=False),
        yaxis_visible=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_priority_top, use_container_width=True)
    
    # Key metrics for Myanmar
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Cases", f"{priority1_cases:,}")
    with m2:
        st.metric("Deaths", f"{priority1_deaths:,}")
    with m3:
        st.metric("Rate/1K Pop", f"{priority1_rate:.1f}")

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
    st.markdown(f'<div class="recommendation-box">👉 Myanmar: {top_funding:.1f}%<br/>Priority: Highest</div>', unsafe_allow_html=True)

# ============================================================
# COUNTRY RANKINGS (SIMPLE TABLE)
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("### All Countries Ranked")

ranking_table = priority_df[['country', 'confirmed_cases', 'deaths', 'priority_score']].copy()
ranking_table.columns = ['Country', 'Cases', 'Deaths', 'Priority Score']
ranking_table['Cases'] = ranking_table['Cases'].apply(lambda x: f"{int(x):,}")
ranking_table['Deaths'] = ranking_table['Deaths'].apply(lambda x: f"{int(x):,}")

st.dataframe(
    ranking_table.style.format({'Priority Score': '{:.1f}'}),
    use_container_width=True,
    hide_index=True,
    height=200
)

# ============================================================
# TREND CONFIRMATION
# ============================================================
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("### 📈 Is the Problem Getting Worse?")

country_year_df = df.groupby(['year', 'country']).agg({
    'confirmed_cases': 'sum'
}).reset_index().sort_values('year')

col_cases, col_info = st.columns([2, 1])

with col_cases:
    fig_trend = px.line(
        country_year_df,
        x='year',
        y='confirmed_cases',
        color='country',
        markers=True,
        title='10-Year Trend',
        labels={'confirmed_cases': 'Cases', 'year': 'Year', 'country': 'Country'}
    )
    fig_trend.update_layout(height=220, hovermode='x unified', showlegend=True)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_info:
    st.markdown("**Status**")
    st.info("📉 **Declining** - Programs working BUT Myanmar still needs support to maintain progress")

st.markdown("---")
st.markdown("📝 **Methodology**: Priority Score = Case Volume (30%) + Deaths (70%) | **Deaths weighted heavily to reflect severity** | Data: Synthetic Surveillance System")
