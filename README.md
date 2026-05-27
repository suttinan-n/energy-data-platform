# 🌤️ Thailand Energy & Weather Data Platform

An end-to-end Data Engineering pipeline that collects, transforms,
and visualizes weather data for Thailand using modern data stack.

## 🛠️ Tech Stack

| Layer           | Tool                   |
| --------------- | ---------------------- |
| Ingestion       | Python, Requests       |
| Storage         | PostgreSQL             |
| Transform       | dbt (Staging + Mart)   |
| Orchestration   | Apache Airflow         |
| Visualization   | Streamlit, Plotly      |
| Infrastructure  | Docker, Docker Compose |
| Version Control | Git, GitHub            |

## 📊 Pipeline Flow

1. **Ingest** — Python fetches daily weather data from Open-Meteo API
2. **Store** — Raw data loaded into PostgreSQL raw_weather table
3. **Transform** — dbt cleans and models data into staging and mart layers
4. **Orchestrate** — Airflow DAG runs the pipeline daily at 06:00
5. **Visualize** — Streamlit dashboard displays KPIs and charts

## 📁 Project Structure

energy-data-platform/
├── dags/ Airflow DAGs
├── ingestion/ Python ingestion scripts
├── dbt_project/ dbt models
│ └── models/
│ ├── staging/ Clean raw data
│ └── mart/ Business-ready data
├── dashboard/ Streamlit dashboard
├── docker-compose.yml Infrastructure
└── requirements.txt Python dependencies

## 🚀 How to Run

```bash
git clone https://github.com/suttinan-n/energy-data-platform.git
cd energy-data-platform
docker compose up -d
python ingestion/fetch_weather.py
cd dbt_project && dbt run
streamlit run dashboard/app.py
```

## 👤 Author

Suttinan Singhad

- LinkedIn: linkedin.com/in/suttinan-singhad
- GitHub: github.com/suttinan-n
