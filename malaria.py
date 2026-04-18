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

# ============================================================
# CLMV COUNTRIES FUNDING ANALYSIS
# ============================================================
st.subheader("🌏 CLMV Countries Funding Needs Analysis")

clmv_countries = ['Cambodia', 'Laos', 'Myanmar', 'Vietnam']
clmv_df = df[df['country'].isin(clmv_countries)].groupby('country').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'population': 'mean'
}).reset_index()

clmv_df['case_rate'] = (clmv_df['confirmed_cases'] / clmv_df['population'] * 1000).round(2)
clmv_df['mortality_rate'] = (clmv_df['deaths'] / clmv_df['population'] * 1000).round(2)
clmv_df['cfr'] = (clmv_df['deaths'] / clmv_df['confirmed_cases'] * 100).round(2)
clmv_df = clmv_df.sort_values('confirmed_cases', ascending=False)

fig_clmv = px.bar(
    clmv_df,
    x='country',
    y='confirmed_cases',
    text='confirmed_cases',
    color='deaths',
    color_continuous_scale="Reds",
    labels={'confirmed_cases': 'Total Cases', 'country': 'Country', 'deaths': 'Deaths'},
    hover_data=['deaths', 'case_rate', 'cfr']
)
fig_clmv.update_layout(height=350, title="CLMV Countries: Total Malaria Burden")
st.plotly_chart(fig_clmv, use_container_width=True)

st.markdown("### CLMV Summary Table")
clmv_summary = clmv_df[['country', 'confirmed_cases', 'deaths', 'cfr', 'case_rate']].copy()
clmv_summary.columns = ['Country', 'Total Cases', 'Total Deaths', 'Case Fatality Rate (%)', 'Case Rate (per 1000)']
st.dataframe(clmv_summary.to_dict('records'), use_container_width=True)

st.markdown("---")

# KPI Cards
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_cases = filtered_df['confirmed_cases'].sum()
total_deaths = filtered_df['deaths'].sum()
total_pf = filtered_df['pf_cases'].sum()
total_pv = filtered_df['pv_cases'].sum()
total_severe = filtered_df['severe_cases'].sum()
cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0

# Calculate trend (compare first and last year)
first_year = int(min(df['year'].unique())) if selected_year == 'All' else selected_year
last_year = int(max(df['year'].unique())) if selected_year == 'All' else selected_year

cases_first = df[(df['year'] == first_year)]['confirmed_cases'].sum()
cases_last = df[(df['year'] == last_year)]['confirmed_cases'].sum()
reduction = ((cases_first - cases_last) / cases_first * 100) if cases_first > 0 else 0

col1.metric("Total Cases", f"{total_cases:,.0f}")
col2.metric("Total Deaths", f"{total_deaths:,.0f}")
col3.metric("Case Fatality Rate", f"{cfr:.2f}%")
col4.metric("Pf Cases", f"{total_pf:,.0f}")
col5.metric("Pv Cases", f"{total_pv:,.0f}")
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
# 10-YEAR TRENDS: Cases & Deaths by Country (Side-by-Side)
# ============================================================
st.subheader("📊 10-Year Trends: Cases & Deaths by Country")

country_year_df = df.groupby(['year', 'country']).agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum'
}).reset_index().sort_values('year')

col_cases, col_deaths = st.columns(2)

with col_cases:
    fig_country_cases = px.line(
        country_year_df,
        x='year',
        y='confirmed_cases',
        color='country',
        markers=True,
        labels={'confirmed_cases': 'Cases', 'year': 'Year', 'country': 'Country'},
        title="Cases by Country (2015-2025)"
    )
    fig_country_cases.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_country_cases, use_container_width=True)

with col_deaths:
    fig_country_deaths = px.line(
        country_year_df,
        x='year',
        y='deaths',
        color='country',
        markers=True,
        labels={'deaths': 'Deaths', 'year': 'Year', 'country': 'Country'},
        title="Deaths by Country (2015-2025)"
    )
    fig_country_deaths.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_country_deaths, use_container_width=True)

# ============================================================
# 10-YEAR TRENDS: Cases & Deaths by Region (Side-by-Side)
# ============================================================
st.subheader("📊 10-Year Trends: Cases & Deaths by Region")

region_year_df = df.groupby(['year', 'region']).agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum'
}).reset_index().sort_values('year')

col_reg_cases, col_reg_deaths = st.columns(2)

with col_reg_cases:
    fig_region_cases = px.line(
        region_year_df,
        x='year',
        y='confirmed_cases',
        color='region',
        markers=True,
        labels={'confirmed_cases': 'Cases', 'year': 'Year', 'region': 'Region'},
        title="Cases by Region (2015-2025)"
    )
    fig_region_cases.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_region_cases, use_container_width=True)

with col_reg_deaths:
    fig_region_deaths = px.line(
        region_year_df,
        x='year',
        y='deaths',
        color='region',
        markers=True,
        labels={'deaths': 'Deaths', 'year': 'Year', 'region': 'Region'},
        title="Deaths by Region (2015-2025)"
    )
    fig_region_deaths.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_region_deaths, use_container_width=True)

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

if len(district_df) > 0:
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
else:
    st.info("No district data available for selected filters.")

# ============================================================
# Border Area Analysis (Geographic Heatmap)
# ============================================================
st.subheader("🚧 Border Area Analysis (Geographic Heatmap)")

# District coordinates mapping (approximate centroids for major districts in CLMV)
district_coords = {
    # Myanmar
    'Bagan': {'lat': 21.17, 'lon': 94.86, 'country': 'Myanmar'},
    'Mandalay': {'lat': 21.97, 'lon': 96.08, 'country': 'Myanmar'},
    'Kalaw': {'lat': 20.44, 'lon': 96.54, 'country': 'Myanmar'},
    'Tachileik': {'lat': 20.44, 'lon': 99.88, 'country': 'Myanmar'},
    'Mawlamyine': {'lat': 16.49, 'lon': 97.64, 'country': 'Myanmar'},
    'Dawei': {'lat': 14.08, 'lon': 98.20, 'country': 'Myanmar'},
    
    # Thailand (for reference)
    'Mae Sai': {'lat': 20.41, 'lon': 100.08, 'country': 'Thailand'},
    'Mae Sot': {'lat': 16.72, 'lon': 98.55, 'country': 'Thailand'},
    
    # Laos
    'Luang Namtha': {'lat': 20.94, 'lon': 101.41, 'country': 'Laos'},
    'Muang Xai': {'lat': 20.73, 'lon': 101.97, 'country': 'Laos'},
    'Vientiane': {'lat': 17.97, 'lon': 102.63, 'country': 'Laos'},
    'Savannakhet': {'lat': 16.56, 'lon': 104.76, 'country': 'Laos'},
    'Pakse': {'lat': 15.12, 'lon': 105.81, 'country': 'Laos'},
    
    # Cambodia
    'Banteay Meanchey': {'lat': 13.74, 'lon': 102.75, 'country': 'Cambodia'},
    'Siem Reap': {'lat': 13.36, 'lon': 103.85, 'country': 'Cambodia'},
    'Stung Treng': {'lat': 13.53, 'lon': 105.97, 'country': 'Cambodia'},
    'Battambang': {'lat': 13.10, 'lon': 103.20, 'country': 'Cambodia'},
    'Phnom Penh': {'lat': 11.56, 'lon': 104.92, 'country': 'Cambodia'},
    
    # Vietnam
    'Hanoi': {'lat': 21.03, 'lon': 105.85, 'country': 'Vietnam'},
    'Ha Giang': {'lat': 22.80, 'lon': 104.98, 'country': 'Vietnam'},
    'Cao Bang': {'lat': 22.88, 'lon': 106.25, 'country': 'Vietnam'},
    'Lang Son': {'lat': 21.86, 'lon': 106.77, 'country': 'Vietnam'},
    'Da Nang': {'lat': 16.07, 'lon': 108.23, 'country': 'Vietnam'},
    'Ho Chi Minh': {'lat': 10.78, 'lon': 106.70, 'country': 'Vietnam'},
}

# Prepare geo data from filtered_df
geo_df = filtered_df.groupby('district').agg({
    'confirmed_cases': 'sum',
    'deaths': 'sum',
    'severe_cases': 'sum',
    'border_crossings': 'sum',
    'is_border_area': 'max'
}).reset_index()

# Add coordinates
geo_df['lat'] = geo_df['district'].apply(lambda x: district_coords.get(x, {}).get('lat', None))
geo_df['lon'] = geo_df['district'].apply(lambda x: district_coords.get(x, {}).get('lon', None))

# Remove rows without coordinates
geo_df = geo_df.dropna(subset=['lat', 'lon'])

if len(geo_df) > 0:
    # Add border area label
    geo_df['area_type'] = geo_df['is_border_area'].map({0: 'Non-Border', 1: 'Border'})
    
    # Select metric for map sizing/coloring
    metric_map = st.selectbox(
        "Select Metric for Geographic Display:",
        options=['Confirmed Cases', 'Deaths', 'Border Crossings']
    )
    
    if metric_map == 'Confirmed Cases':
        size_col = 'confirmed_cases'
        color_col = 'confirmed_cases'
        title = "Geographic Heatmap: Malaria Cases by District"
    elif metric_map == 'Deaths':
        size_col = 'deaths'
        color_col = 'deaths'
        title = "Geographic Heatmap: Malaria Deaths by District"
    else:
        size_col = 'border_crossings'
        color_col = 'border_crossings'
        title = "Geographic Heatmap: Border Crossings by District"
    
    fig4 = px.scatter_mapbox(
        geo_df,
        lat='lat',
        lon='lon',
        size=size_col,
        color=color_col,
        hover_name='district',
        hover_data={
            'confirmed_cases': ':,',
            'deaths': ':,',
            'border_crossings': ':,',
            'area_type': True,
            'lat': ':.2f',
            'lon': ':.2f'
        },
        color_continuous_scale='Reds',
        size_max=50,
        zoom=4,
        center={'lat': 16, 'lon': 101},
        mapbox_style='open-street-map',
        title=title
    )
    
    fig4.update_layout(height=600)
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No geographic data available for selected filters.")

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
    (summary_df['confirmed_cases'] / summary_df['confirmed_cases'].max() * 30 if summary_df['confirmed_cases'].max() > 0 else 0) +
    (summary_df['deaths'] / summary_df['deaths'].max() * 30 if summary_df['deaths'].max() > 0 else 0) +
    (summary_df['severe_cases'] / summary_df['severe_cases'].max() * 20 if summary_df['severe_cases'].max() > 0 else 0) +
    (summary_df['border_crossings'] / summary_df['border_crossings'].max() * 20 if summary_df['border_crossings'].max() > 0 else 0)
).round(1)

total_priority = summary_df['priority_score'].sum()
summary_df['funding_allocation'] = (
    (summary_df['priority_score'] / total_priority * 100) if total_priority > 0 else 0
).round(1)

summary_df = summary_df.sort_values('priority_score', ascending=False)

# Determine label column
label_col = 'country' if 'country' in summary_df.columns and len(summary_df) > 1 else 'region'

if len(summary_df) > 0:
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
else:
    st.warning("No data available to calculate resource allocation.")

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown("**Data Source:** Malaria Surveillance System (2015-2025)")
st.markdown("**Dashboard for Funding Agency Resource Allocation**")
