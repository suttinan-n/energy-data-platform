import requests
import psycopg2
import pandas as pd
from datetime import datetime

# ── 1. ดึงข้อมูลจาก Open-Meteo API ──────────────────────
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 13.75,
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
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("❌ API timeout after 30 seconds")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"❌ HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ API Error: {e}")

# ── 2. แปลงข้อมูลเป็น DataFrame ─────────────────────────
def transform_weather(data):
    if "daily" not in data:
        raise ValueError("❌ Invalid data format: missing 'daily' key")
    
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

    # ตรวจสอบข้อมูลก่อน load
    if df.empty:
        raise ValueError("❌ No data to load")
    if df["temp_max"].isnull().any():
        raise ValueError("❌ temp_max contains null values")
    if df["temp_min"].isnull().any():
        raise ValueError("❌ temp_min contains null values")

    return df

# ── 3. บันทึกลง PostgreSQL ───────────────────────────────
def load_to_postgres(df):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="airflow",
            user="airflow",
            password="airflow"
        )
    except psycopg2.OperationalError as e:
        raise Exception(f"❌ Cannot connect to PostgreSQL: {e}")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_weather (
                id SERIAL PRIMARY KEY,
                date DATE,
                temp_max FLOAT,
                temp_min FLOAT,
                precipitation FLOAT,
                windspeed_max FLOAT,
                location VARCHAR(100),
                created_at TIMESTAMP,
                UNIQUE(date, location)
            )
        """)

        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO raw_weather 
                    (date, temp_max, temp_min, precipitation, 
                     windspeed_max, location, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date, location) DO NOTHING
                """, (
                    row["date"], row["temp_max"], row["temp_min"],
                    row["precipitation"], row["windspeed_max"],
                    row["location"], row["created_at"]
                ))
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"⚠️ Skipping row {row['date']}: {e}")
                continue

        conn.commit()
        print(f"✅ Inserted: {inserted} rows | Skipped (duplicate): {skipped} rows")

    except Exception as e:
        conn.rollback()
        raise Exception(f"❌ Database error: {e}")
    finally:
        cursor.close()
        conn.close()

# ── 4. รันทั้งหมด ─────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("🔄 Fetching weather data...")
        data = fetch_weather()

        print("🔄 Transforming data...")
        df = transform_weather(data)
        print(df)

        print("🔄 Loading to PostgreSQL...")
        load_to_postgres(df)

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise