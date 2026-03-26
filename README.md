# NYC Taxi Trip & Weather Data Warehouse Analysis

An End-to-End Data Engineering project focused on building a scalable Data Warehouse using Python and PostgreSQL.

<p align="center">
  <a href="#bahasa-indonesia">
    <img src="https://img.shields.io/badge/Lang-Indonesia-red?style=for-the-badge&logo=google-translate&logoColor=white" alt="Bahasa Indonesia">
  </a>
  <a href="#english-version">
    <img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge&logo=google-translate&logoColor=white" alt="English">
  </a>
</p>

---
## Bahasa Indonesia


### 🎯 Tujuan Proyek
Proyek ini dikembangkan sebagai sarana pembelajaran untuk mendalami konsep dan proses pembuatan **Data Pipeline** serta **Data Warehouse**. Fokus utama dari proyek ini adalah:
* Memahami arsitektur pipeline data (Extract, Transform, Load).
* Implementasi *Star Schema* dalam pemodelan data.
* Integrasi data dari berbagai sumber (API, Parquet, dan CSV).
* Penanganan kualitas data (Data Cleaning) menggunakan Pandas.

### 🚀 Teknologi yang Digunakan
* **Bahasa Pemrograman:** Python 3.11.9
* **Database:** PostgreSQL
* **Library Utama:**
    * `Pandas`: Manipulasi dan pembersihan data.
    * `Requests`: Pengambilan data dari API.
    * `Logging`: Monitoring dan audit proses ETL.
    * `SQLAlchemy / Psycopg2`: Konektivitas database.

### 📊 Sumber Data
1.  **Trip Record:** [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) (Format Parquet).
2.  **Taxi Zone:** [TLC Zone Mapping](https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv) (Format CSV).
3.  **Weather Data:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (Format JSON).

### 🗂️ Model Data (ERD)
Proyek ini mengimplementasikan **Star Schema** untuk optimalisasi query analitik:
* **Fact Table:** `fact_taxi_trips`
* **Dimension Tables:** `dim_weather`, `dim_location`, `dim_datetime`, `dim_payment`.
<p align="center">
  <img src="document\ERD Diagram.png" alt="Schema ERD" width="600">
</p>

### 🛠️ Cara Penggunaan
1.  **Persiapan Database:** Jalankan file SQL untuk membuat struktur tabel di PostgreSQL.
    ```bash
    psql -U username -d db_name -f sql/create_tables.sql
    ```
2.  **Eksekusi Pipeline:** Jalankan skrip utama untuk memulai proses Extract, Transform, dan Load.
    ```bash
    python main.py
    ```
3.  **Monitoring:** Pantau progres proses melalui file di direktori `/logs`.

---

## English Version

### 🎯 Project Objectives
This project is developed as a learning platform to explore the concepts and processes of building a **Data Pipeline** and a **Data Warehouse**. The key focus areas are:
* Understanding data pipeline architecture (Extract, Transform, Load).
* Implementing *Star Schema* for data modeling.
* Integrating data from multiple sources (API, Parquet, and CSV).
* Ensuring data quality through cleaning and standardization using Pandas.

### 🚀 Technologies Used
* **Programming Language:** Python 3.11.9
* **Database:** PostgreSQL
* **Key Libraries:**
    * `Pandas`: Data manipulation and cleaning.
    * `Requests`: API data ingestion.
    * `Logging`: Monitoring and auditing the ETL process.
    * `SQLAlchemy / Psycopg2`: Database connectivity.

### 📊 Data Sources
1.  **Trip Record:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) (Parquet format).
2.  **Taxi Zone:** [TLC Zone Mapping](https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv) (CSV format).
3.  **Weather Data:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (JSON format).

### 🗂️ Data Model (ERD)
The project implements a **Star Schema** designed for analytical query optimization:
* **Fact Table:** `fact_taxi_trips`
* **Dimension Tables:** `dim_weather`, `dim_location`, `dim_datetime`, `dim_payment`.
<p align="center">
  <img src="document\ERD Diagram.png" alt="Schema ERD" width="600">
</p>

### 🛠️ Usage
1.  **Database Setup:** Execute the SQL file to create the necessary table structures in PostgreSQL.
    ```bash
    psql -U username -d db_name -f sql/create_tables.sql
    ```
2.  **Run Pipeline:** Execute the main script to start the ETL (Extract, Transform, Load) process.
    ```bash
    python main.py
    ```
3.  **Monitoring:** Monitor the process progress via the files in the `/logs` directory.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

**Author:** Bimo Abdul Aziz