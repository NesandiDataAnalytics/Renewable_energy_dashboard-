import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Renewable Energy Dashboard", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 8px 0;
        font-size: 15px;
    }
    .header-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 30px 40px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 24px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 3px solid #2ecc71;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("renewable_energy_cleaned.csv")
    return df

df = load_data()

# ── HERO HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1 style="margin:0;font-size:2.2rem;">⚡ Global Renewable Energy Dashboard</h1>
    <p style="margin:10px 0 0 0;opacity:0.85;font-size:1rem;">
        Exploring installed renewable electricity-generating capacity (watts per capita) across 222 countries · 2000–2022 · World Bank SE4ALL
    </p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Use the filters below to explore the data.")

all_sources = sorted(df['Energy_Source'].unique().tolist())
default_idx = all_sources.index("All renewables") if "All renewables" in all_sources else 0
selected_source = st.sidebar.selectbox("⚡ Energy Source", all_sources, index=default_idx)

year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
selected_year = st.sidebar.slider("📅 Year", year_min, year_max, year_max)

top_n = st.sidebar.slider("🏆 Top N Countries", 5, 30, 15)

all_countries = sorted(df['Country'].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "🌍 Compare Countries (trend chart)",
    all_countries,
    default=["China", "United States", "Germany", "India", "Brazil"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data source:** [World Bank SE4ALL](https://data360.worldbank.org/en/indicator/WB_SE4ALL_EG_EGEN_RNEW)")

# ── DATA FILTERING ────────────────────────────────────────────────────────────
filtered = df[df['Energy_Source'] == selected_source]
year_data = filtered[filtered['Year'] == selected_year].dropna()
top_countries_df = year_data.nlargest(top_n, 'Capacity_W_per_capita')
leader = top_countries_df.iloc[0] if len(top_countries_df) > 0 else None

st.info("👈 Sidebar filters added! Key metrics and charts coming next...")