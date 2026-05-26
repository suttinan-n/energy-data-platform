import requests
import psycopg2
import pandas as pd
from datetime import datetime

# ── 1. ดึงข้อมูลจาก Open-Meteo API ──────────────────────
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 13.75,   # กรุงเทพฯ
        "longitude": 100.52,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max"
        ],
        "timezone": "Asia/Bangkok",
        "forecast_days": 7
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# ── 2. แปลงข้อมูลเป็น DataFrame ─────────────────────────
def transform_weather(data):
    daily = data["daily"]
    df = pd.DataFrame({
        "date": daily["time"],
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "precipitation": daily["precipitation_sum"],
        "windspeed_max": daily["windspeed_10m_max"],
        "location": "Bangkok",
        "created_at": datetime.now()
    })
    return df

# ── 3. บันทึกลง PostgreSQL ───────────────────────────────
def load_to_postgres(df):
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cursor = conn.cursor()

    # สร้าง table ถ้ายังไม่มี
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_weather (
            id SERIAL PRIMARY KEY,
            date DATE,
            temp_max FLOAT,
            temp_min FLOAT,
            precipitation FLOAT,
            windspeed_max FLOAT,
            location VARCHAR(100),
            created_at TIMESTAMP
        )
    """)

    # insert ข้อมูลทีละแถว
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO raw_weather 
            (date, temp_max, temp_min, precipitation, windspeed_max, location, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row["date"], row["temp_max"], row["temp_min"],
            row["precipitation"], row["windspeed_max"],
            row["location"], row["created_at"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Loaded {len(df)} rows to PostgreSQL")

# ── 4. รันทั้งหมด ─────────────────────────────────────────
if __name__ == "__main__":
    print("🔄 Fetching weather data...")
    data = fetch_weather()
    
    print("🔄 Transforming data...")
    df = transform_weather(data)
    print(df)
    
    print("🔄 Loading to PostgreSQL...")
    load_to_postgres(df)