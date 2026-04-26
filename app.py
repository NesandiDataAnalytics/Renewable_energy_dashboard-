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

st.markdown("""
<div class="header-box">
    <h1 style="margin:0;font-size:2.2rem;">⚡ Global Renewable Energy Dashboard</h1>
    <p style="margin:10px 0 0 0;opacity:0.85;font-size:1rem;">
        Exploring installed renewable electricity-generating capacity (watts per capita) across 222 countries · 2000–2022 · World Bank SE4ALL
    </p>
</div>
""", unsafe_allow_html=True)

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
st.sidebar.markdown("**Data source:** [World Bank SE4ALL](https://data360.worldbank.org/en/indicator/WB_SE4ALL_EG_IGEN_RNEW)")

filtered = df[df['Energy_Source'] == selected_source]
year_data = filtered[filtered['Year'] == selected_year].dropna()
top_countries_df = year_data.nlargest(top_n, 'Capacity_W_per_capita')
leader = top_countries_df.iloc[0] if len(top_countries_df) > 0 else None

st.markdown('<p class="section-title">📊 Key Metrics</p>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌍 Countries with data", len(year_data))
col2.metric("🏆 Highest capacity",
    f"{top_countries_df['Capacity_W_per_capita'].max():,.0f} W/capita" if leader is not None else "N/A")
col3.metric("📈 Global average",
    f"{year_data['Capacity_W_per_capita'].mean():,.1f} W/capita")
col4.metric("📅 Selected year", selected_year)

st.markdown("---")

# ── KEY INSIGHTS ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">💡 Key Insights</p>', unsafe_allow_html=True)

if leader is not None:
    avg = year_data['Capacity_W_per_capita'].mean()
    top_val = leader['Capacity_W_per_capita']
    times_above = top_val / avg if avg > 0 else 0
    bottom_country = year_data.nsmallest(1, 'Capacity_W_per_capita').iloc[0]
    prev_year_data = filtered[filtered['Year'] == selected_year - 1].dropna()
    if not prev_year_data.empty:
        prev_avg = prev_year_data['Capacity_W_per_capita'].mean()
        growth = ((avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        growth_text = f"Global average capacity grew by {growth:.1f}% compared to {selected_year - 1}."
    else:
        growth_text = "Select a year after 2000 to see growth."

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        st.markdown(f"""<div class="insight-box">
            🥇 <b>Leading country:</b> {leader['Country']} with {top_val:,.0f} W/capita —
            that's {times_above:.1f}x the global average!
        </div>""", unsafe_allow_html=True)
    with col_i2:
        st.markdown(f"""<div class="insight-box">
            📉 <b>Lowest capacity:</b> {bottom_country['Country']} with only
            {bottom_country['Capacity_W_per_capita']:,.1f} W/capita,
            showing a huge gap between nations.
        </div>""", unsafe_allow_html=True)
    with col_i3:
        st.markdown(f"""<div class="insight-box">
            📈 <b>Year-on-year trend:</b> {growth_text}
        </div>""", unsafe_allow_html=True)

st.markdown("---")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown(f'<p class="section-title">🏆 Top {top_n} Countries in {selected_year}</p>', unsafe_allow_html=True)
    fig_bar = px.bar(
        top_countries_df.sort_values('Capacity_W_per_capita'),
        x='Capacity_W_per_capita', y='Country', orientation='h',
        color='Capacity_W_per_capita', color_continuous_scale='Teal',
        labels={'Capacity_W_per_capita': 'Watts per capita', 'Country': ''},
        template='plotly_white')
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False, height=480,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(size=13))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.markdown(f'<p class="section-title">🔋 Energy Source Breakdown in {selected_year}</p>', unsafe_allow_html=True)
    source_data = df[(df['Year'] == selected_year) & (df['Country'].isin(top_countries_df['Country'].tolist()))]
    pie_data = source_data[source_data['Energy_Source'] != 'All renewables']\
        .groupby('Energy_Source')['Capacity_W_per_capita'].mean().reset_index()
    fig_pie = px.pie(pie_data, values='Capacity_W_per_capita', names='Energy_Source',
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2, template='plotly_white')
    fig_pie.update_layout(height=480, paper_bgcolor='rgba(0,0,0,0)', font=dict(size=13),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

st.markdown('<p class="section-title">📈 Trends Over Time — Country Comparison</p>', unsafe_allow_html=True)
if selected_countries:
    trend_data = filtered[filtered['Country'].isin(selected_countries)].dropna()
    fig_line = px.line(trend_data, x='Year', y='Capacity_W_per_capita', color='Country',
        markers=True, labels={'Capacity_W_per_capita': 'Watts per capita', 'Year': 'Year'},
        color_discrete_sequence=px.colors.qualitative.Set1, template='plotly_white')
    fig_line.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified', font=dict(size=13),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25))
    fig_line.update_traces(line=dict(width=2.5), marker=dict(size=6))
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("👈 Select countries in the sidebar to compare trends over time.")

st.markdown("---")

st.markdown(f'<p class="section-title">🌍 World Map — Renewable Capacity in {selected_year}</p>', unsafe_allow_html=True)
fig_map = px.choropleth(year_data.dropna(), locations='Country', locationmode='country names',
    color='Capacity_W_per_capita', color_continuous_scale='YlOrRd',
    labels={'Capacity_W_per_capita': 'W per capita'}, template='plotly_white')
fig_map.update_layout(height=500,
    geo=dict(showframe=False, showcoastlines=True, coastlinecolor='lightgrey', bgcolor='rgba(0,0,0,0)'),
    paper_bgcolor='rgba(0,0,0,0)', coloraxis_colorbar=dict(title="W/capita", thickness=15))
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

st.markdown('<p class="section-title">🔎 Explore Raw Data</p>', unsafe_allow_html=True)
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    search = st.text_input("Search by country name", placeholder="e.g. Germany, China, Brazil...")
with col_t2:
    show_all_years = st.checkbox("Show all years", value=False)

table_data = filtered.copy() if show_all_years else year_data.copy()
if search:
    table_data = table_data[table_data['Country'].str.contains(search, case=False, na=False)]

table_data = table_data.sort_values('Capacity_W_per_capita', ascending=False).reset_index(drop=True)
table_data.index += 1
table_data['Capacity_W_per_capita'] = table_data['Capacity_W_per_capita'].round(2)

st.dataframe(table_data, use_container_width=True, height=350,
    column_config={
        "Country": st.column_config.TextColumn("Country"),
        "Energy_Source": st.column_config.TextColumn("Energy Source"),
        "Year": st.column_config.NumberColumn("Year", format="%d"),
        "Capacity_W_per_capita": st.column_config.ProgressColumn(
            "Capacity (W/capita)", min_value=0,
            max_value=float(df['Capacity_W_per_capita'].max()), format="%.1f")
    })

st.markdown("---")
st.caption("Data source: World Bank Sustainable Energy For All (SE4ALL) · Indicator: WB_SE4ALL_EG_EGEN_RNEW · Built with Streamlit & Plotly")