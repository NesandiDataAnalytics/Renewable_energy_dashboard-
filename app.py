import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Renewable Energy Dashboard", page_icon="⚡", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("renewable_energy_cleaned.csv")
    return df

df = load_data()

st.title("⚡ Global Renewable Energy Dashboard")
st.markdown("**Installed renewable electricity-generating capacity (watts per capita) · World Bank SE4ALL**")
st.markdown("---")
st.write("Dashboard under construction...")