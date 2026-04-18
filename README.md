# Malaria Burden Dashboard

Interactive dashboard for malaria burden data visualization, targeting **funding agency resource allocation**.

## Features

- **KPI Cards**: Total cases, deaths, Pf, Pv, trend indicator
- **Country Overview**: Bar chart showing cases by country (sorted highest first)
- **Time Series**: Confirmed cases, Pf, Pv, severe, deaths over time
- **Regional Analysis**: Cases by region with case rate heatmap
- **Pf vs Pv Comparison**: Species comparison by region
- **Border Area Analysis**: Correlation with migration data
- **Resource Allocation**: Priority scoring and funding recommendations

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo and deploy

## Data

Data source: Malaria Surveillance System (2015-2025)