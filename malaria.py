"""
Malaria Burden Visualization Dashboard
Target: Funding Agency Resource Allocation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Malaria Dashboard | Funding Allocation",
    page_icon="🦟",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("burden_cleaned.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    # Fill missing numeric values with 0
    numeric_cols = ['confirmed_cases', 'pf_cases', 'pv_cases', 'severe_cases', 'deaths', 
                    'border_crossings', 'migrants_in', 'migrants_out', 'population']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Country filter - PRIMARY (dropdown)
all_countries = ['All'] + sorted(df['country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox(
    "Select Country",
    options=all_countries
)

# Year filter (dropdown)
all_years = ['All'] + sorted([int(y) for y in df['year'].unique()])
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=all_years
)

# Region filter (dropdown)
all_regions = ['All'] + sorted(df['region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox(
    "Select Region",
    options=all_regions
)

# District filter (dropdown)
all_districts = ['All'] + sorted(df['district'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox(
    "Select District",
    options=all_districts
)

# Endemic level filter (dropdown)
all_endemic = ['All'] + sorted(df['endemic_level'].dropna().unique().tolist())
selected_endemic = st.sidebar.selectbox(
    "Endemic Level",
    options=all_endemic
)

# Filter data (handle "All" selections)
def filter_data():
    mask = pd.Series([True] * len(df))
    
    if selected_country != 'All':
        mask &= (df['country'] == selected_country)
    
    if selected_year != 'All':
        mask &= (df['year'] == selected_year)
    
    if selected_region != 'All':
        mask &= (df['region'] == selected_region)
    
    if selected_district != 'All':
        mask &= (df['district'] == selected_district)
    
    if selected_endemic != 'All':
        mask &= (df['endemic_level'] == selected_endemic)
    
    return df[mask]

filtered_df = filter_data()

# Main title
st.title("🦟 Malaria Burden Dashboard")
st.markdown("**Target: Funding Agency Resource Allocation**")
st.markdown("**Answer: Which country needs most funding?**")
st.markdown("---")

# KPI Cards
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_cases = filtered_df['confirmed_cases'].sum()
total_deaths = filtered_df['deaths'].sum()
total_pf = filtered_df['pf_cases'].sum()
total_pv = filtered_df['pv_cases'].sum()
total_severe = filtered_df['severe_cases'].sum()

# Calculate trend (compare first and last year)
first_year = int(min(df['year'].unique())) if selected_year == 'All' else selected_year
last_year = int(max(df['year'].unique())) if selected_year == 'All' else selected_year

cases_first = df[(df['year'] == first_year)]['confirmed_cases'].sum()
cases_last = df[(df['year'] == last_year)]['confirmed_cases'].sum()
reduction = ((cases_first - cases_last) / cases_first * 100) if cases_first > 0 else 0

col1.metric("Total Cases", f"{total_cases:,.0f}")
col2.metric("Deaths", f"{total_deaths:,.0f}")
col3.metric("Pf Cases", f"{total_pf:,.0f}")
col4.metric("Pv Cases", f"{total_pv:,.0f}")
col5.metric("Severe", f"{total_severe:,.0f}")
col6.metric(f"Trend ({first_year}→{last_year})", f"{reduction:.1f}%")

st.markdown("---")

# ============================================================
# KEY VISUALIZATION: Country Overview Bar Chart
# ============================================================
st.subheader("🌍 Which Country Needs Most Funding?")

country_df = filtered_df.groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'pf_cases': 'sum',
    'pv_cases': 'sum',
    'population': 'mean'
}).reset_index()

country_df['case_rate'] = (country_df['confirmed_cases'] / country_df['population'] * 1000).round(2)
country_df = country_df.sort_values('confirmed_cases', ascending=False)

fig_country = px.bar(
    country_df,
    x='country',
    y='confirmed_cases',
    text='confirmed_cases',
    color='deaths',
    color_continuous_scale="Reds",
    labels={
        'confirmed_cases': 'Confirmed Cases',
        'country': 'Country',
        'deaths': 'Deaths',
        'case_rate': 'Cases per 1000'
    },
    hover_data=['deaths', 'severe_cases', 'case_rate']
)
fig_country.update_layout(height=400)
st.plotly_chart(fig_country, use_container_width=True)

# ============================================================
# Time Series Chart
# ============================================================
st.subheader("📈 Cases & Deaths Over Time")

agg_df = filtered_df.groupby(['year', 'month']).agg({
    'confirmed_cases': 'sum',
    'pf_cases': 'sum',
    'pv_cases': 'sum',
    'severe_cases': 'sum',
    'deaths': 'sum'
}).reset_index()

agg_df['period'] = agg_df['year'].astype(str) + '-' + agg_df['month'].astype(str).str.zfill(2)
agg_df = agg_df.sort_values(['year', 'month'])

# Show only year on x-axis to avoid crowding
agg_df['year_label'] = agg_df['year'].astype(str)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=agg_df['period'], y=agg_df['confirmed_cases'], 
                          name="Confirmed", line=dict(color='#1f77b4'), hovertemplate='%{x}<br>Cases: %{y:,}<extra></extra>'))
fig1.add_trace(go.Scatter(x=agg_df['period'], y=agg_df['pf_cases'], 
                          name="P. falciparum", line=dict(color='#d62728'), hovertemplate='%{x}<br>Cases: %{y:,}<extra></extra>'))
fig1.add_trace(go.Scatter(x=agg_df['period'], y=agg_df['pv_cases'], 
                          name="P. vivax", line=dict(color='#2ca02c'), hovertemplate='%{x}<br>Cases: %{y:,}<extra></extra>'))
fig1.add_trace(go.Scatter(x=agg_df['period'], y=agg_df['deaths'], 
                          name="Deaths", line=dict(color='#ff7f0e', width=3), hovertemplate='%{x}<br>Deaths: %{y:,}<extra></extra>'))

fig1.update_layout(
    xaxis_title="Period",
    yaxis_title="Cases",
    legend_title="Metric",
    hovermode="x unified",
    height=400,
    xaxis=dict(tickangle=-45),
    showlegend=True
)

st.plotly_chart(fig1, use_container_width=True)

# ============================================================
# Two column layout: Regional & Species
# ============================================================
col_left, col_right = st.columns(2)

# Regional Distribution
with col_left:
    st.subheader("🗺️ Cases by Region")
    region_df = filtered_df.groupby('region').agg({
        'confirmed_cases': 'sum',
        'deaths': 'sum',
        'population': 'mean'
    }).reset_index()
    region_df['case_rate'] = (region_df['confirmed_cases'] / region_df['population'] * 1000).round(2)
    region_df = region_df.sort_values('confirmed_cases', ascending=False)
    
    fig2 = px.bar(
        region_df, 
        x='region', 
        y='confirmed_cases',
        color='case_rate',
        color_continuous_scale="Reds",
        labels={'confirmed_cases': 'Confirmed Cases', 'region': 'Region', 'case_rate': 'Cases per 1000'}
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Pf vs Pv Comparison
with col_right:
    st.subheader("🔬 Pf vs Pv Comparison")
    pv_df = filtered_df.groupby('region').agg({
        'pf_cases': 'sum',
        'pv_cases': 'sum'
    }).reset_index()
    pv_df = pv_df.sort_values('pf_cases', ascending=False)
    
    fig3 = px.bar(
        pv_df,
        x='region',
        y=['pf_cases', 'pv_cases'],
        barmode='group',
        labels={'value': 'Cases', 'variable': 'Species', 'region': 'Region'},
        color_discrete_map={'pf_cases': '#d62728', 'pv_cases': '#2ca02c'}
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# District Ranking
# ============================================================
st.subheader("📍 District Ranking (Where to Focus)")

district_df = filtered_df.groupby('district').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'border_crossings': 'sum',
    'population': 'mean'
}).reset_index()

district_df['case_rate'] = (district_df['confirmed_cases'] / district_df['population'] * 1000).round(2)
district_df = district_df.sort_values('confirmed_cases', ascending=False).head(15)

fig_district = px.bar(
    district_df,
    x='district',
    y='confirmed_cases',
    text='confirmed_cases',
    color='deaths',
    color_continuous_scale="Reds",
    labels={'confirmed_cases': 'Confirmed Cases', 'district': 'District', 'deaths': 'Deaths'},
    hover_data=['case_rate', 'border_crossings']
)
fig_district.update_layout(height=400)
st.plotly_chart(fig_district, use_container_width=True)

# ============================================================
# Border Area Analysis (Matrix Heatmap)
# ============================================================
st.subheader("🚧 Border Area Analysis (Matrix Heatmap)")

# Create pivot table: Region x Border Area Type
matrix_df = filtered_df.groupby(['region', 'is_border_area']).agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'border_crossings': 'sum',
    'migrants_in': 'sum',
    'severe_cases': 'sum'
}).reset_index()

matrix_df['area_type'] = matrix_df['is_border_area'].map({0: 'Non-Border', 1: 'Border'})

# Create matrix for confirmed cases
cases_matrix = matrix_df.pivot_table(
    index='region', 
    columns='area_type', 
    values='confirmed_cases', 
    fill_value=0
)

# Create matrix for border crossings
crossings_matrix = matrix_df.pivot_table(
    index='region', 
    columns='area_type', 
    values='border_crossings', 
    fill_value=0
)

# Create matrix for deaths
deaths_matrix = matrix_df.pivot_table(
    index='region', 
    columns='area_type', 
    values='deaths', 
    fill_value=0
)

# Select matrix to display
metric_options = ['Confirmed Cases', 'Border Crossings', 'Deaths']
selected_metric = st.selectbox("Select Metric for Heatmap:", metric_options)

if selected_metric == 'Confirmed Cases':
    display_matrix = cases_matrix
    title = "Cases by Region & Border Area"
elif selected_metric == 'Border Crossings':
    display_matrix = crossings_matrix
    title = "Border Crossings by Region & Area Type"
else:
    display_matrix = deaths_matrix
    title = "Deaths by Region & Border Area"

# Create heatmap
fig4 = go.Figure(data=go.Heatmap(
    z=display_matrix.values,
    x=display_matrix.columns.tolist(),
    y=display_matrix.index.tolist(),
    colorscale='Reds',
    text=display_matrix.values,
    texttemplate='%{text:,}',
    hovertemplate='Region: %{y}<br>Area: %{x}<br>Value: %{z:,}<extra></extra>'
))

fig4.update_layout(
    title=title,
    xaxis_title="Area Type",
    yaxis_title="Region",
    height=max(400, len(display_matrix) * 40),
    margin=dict(l=150)
)

st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# Resource Allocation Summary
# ============================================================
st.subheader("💰 Resource Allocation Summary (Priority Score)")

# Calculate priority score based on cases, deaths, severe, and border activity
summary_df = filtered_df.groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'border_crossings': 'sum',
    'population': 'mean'
}).reset_index()

# If only one country, break down by region instead
if len(summary_df) == 1:
    summary_df = filtered_df.groupby('region').agg({
        'confirmed_cases': 'sum',
        'deaths': 'sum',
        'severe_cases': 'sum',
        'border_crossings': 'sum',
        'population': 'mean'
    }).reset_index()

summary_df['priority_score'] = (
    (summary_df['confirmed_cases'] / summary_df['confirmed_cases'].max() * 30) +
    (summary_df['deaths'] / summary_df['deaths'].max() * 30) +
    (summary_df['severe_cases'] / summary_df['severe_cases'].max() * 20) +
    (summary_df['border_crossings'] / summary_df['border_crossings'].max() * 20)
).round(1)

summary_df['funding_allocation'] = (
    summary_df['priority_score'] / summary_df['priority_score'].sum() * 100
).round(1)

summary_df = summary_df.sort_values('priority_score', ascending=False)

# Determine label column
label_col = 'country' if 'country' in summary_df.columns and len(summary_df) > 1 else 'region'

fig5 = px.bar(
    summary_df,
    x=label_col,
    y='funding_allocation',
    text='funding_allocation',
    labels={'funding_allocation': 'Funding Allocation (%)', label_col: label_col.title()},
    color='priority_score',
    color_continuous_scale="Reds"
)
fig5.update_layout(height=350)
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown("**Data Source:** Malaria Surveillance System (2015-2025)")
st.markdown("**Dashboard for Funding Agency Resource Allocation**")
