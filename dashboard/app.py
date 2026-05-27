import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Thailand Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# ── Connect PostgreSQL ────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    df = pd.read_sql("""
        SELECT *
        FROM staging_mart.mart_weather_daily
        ORDER BY weather_date
    """, conn)
    conn.close()
    return df

# ── Load Data ─────────────────────────────────────────────
df = load_data()

# ── Header ────────────────────────────────────────────────
st.title("🌤️ Thailand Weather Dashboard")
st.caption("Data powered by Open-Meteo API | Pipeline: Airflow + dbt + PostgreSQL")

st.divider()

# ── KPI Cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌡️ Max Temp", f"{df['temp_max_celsius'].max():.1f}°C")
with col2:
    st.metric("🌡️ Min Temp", f"{df['temp_min_celsius'].min():.1f}°C")
with col3:
    st.metric("🌧️ Total Rain", f"{df['precipitation_mm'].sum():.1f} mm")
with col4:
    st.metric("💨 Max Wind", f"{df['windspeed_max_kmh'].max():.1f} km/h")

st.divider()

# ── Charts ────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌡️ Temperature Trend")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=df['weather_date'], y=df['temp_max_celsius'],
        name='Max Temp', line=dict(color='red')
    ))
    fig_temp.add_trace(go.Scatter(
        x=df['weather_date'], y=df['temp_min_celsius'],
        name='Min Temp', line=dict(color='blue')
    ))
    fig_temp.add_trace(go.Scatter(
        x=df['weather_date'], y=df['temp_avg_celsius'],
        name='Avg Temp', line=dict(color='orange', dash='dash')
    ))
    fig_temp.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

with col_right:
    st.subheader("🌧️ Precipitation")
    fig_rain = px.bar(
        df, x='weather_date', y='precipitation_mm',
        color='rain_category',
        color_discrete_map={
            'No Rain': '#87CEEB',
            'Light Rain': '#4169E1',
            'Moderate Rain': '#0000CD',
            'Heavy Rain': '#00008B'
        }
    )
    fig_rain.update_layout(xaxis_title="Date", yaxis_title="Precipitation (mm)")
    st.plotly_chart(fig_rain, use_container_width=True)

# ── Data Table ────────────────────────────────────────────
st.subheader("📋 Raw Data")
st.dataframe(df, use_container_width=True)