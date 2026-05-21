import pandas as pd
import numpy as np
import json
import os
import re

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger


def transform_zone(file_path: str):
    """Transform taxi zone lookup CSV into dim_location DataFrame."""
    file_name = os.path.basename(file_path)

    logger.info(f"TRANSFORM START: Processing {file_name}")
    logger.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        df_clean = pd.read_csv(file_path)
        logger.info(f"STEP [1/4]     : CSV data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Drop Irrelevant Column
        df_clean.drop(columns=['service_zone'], inplace=True)
        logger.info(f"STEP [2/4]     : Dropped 'service_zone' column.")

        # [3] Text Standardization
        df_clean['Borough'] = df_clean['Borough'].str.strip().str.title()
        df_clean['Zone'] = df_clean['Zone'].str.strip().str.title()
        logger.info(f"STEP [3/4]     : Standardized 'Borough' and 'Zone' (Strip & Title Case).")

        # [4] Renaming
        df_clean.rename(
            columns={
                'LocationID': 'location_id',
                'Borough': 'borough',
                'Zone': 'zone'
            },
            inplace=True
        )
        logger.info(f"STEP [4/4]     : Renamed columns to match database schema.")

        logger.info(f"TRANSFORM SUCCESS: {file_name} is ready. Final rows: {len(df_clean)}")
        return df_clean

    except Exception as e:
        logger.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None


# Alias agar konsisten dengan pemanggilan di main.py
transform_location = transform_zone


def transform_trip_data(file_path: str):
    """Transform raw trip parquet into (dim_datetime, fact_taxi_trips) DataFrames."""
    file_name = os.path.basename(file_path)

    file_info = re.search(r'(\d{4})-(\d{2})', file_name)
    if not file_info:
        logger.error(f"TRANSFORM FAILED : Cannot parse year/month from filename: {file_name}")
        return None

    target_year = int(file_info.group(1))
    target_month = int(file_info.group(2))

    logger.info(f"TRANSFORM START: Processing {file_name}")
    logger.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        df_clean = pd.read_parquet(file_path)
        logger.info(f"STEP [1/7]     : Parquet data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Drop Irrelevant Columns
        cols_to_drop = [
            'VendorID', 'RatecodeID', 'store_and_fwd_flag', 'extra',
            'mta_tax', 'tolls_amount', 'improvement_surcharge',
            'congestion_surcharge', 'airport_fee'
        ]
        df_clean.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        logger.info(f"STEP [2/7]     : Removed irrelevant columns.")

        # [3] Data Validation & Cleaning
        initial_rows = len(df_clean)

        # Impute passenger_count: replace 0/null with mode
        mode_passenger = df_clean['passenger_count'].mode()[0]
        df_clean['passenger_count'] = (
            df_clean['passenger_count'].replace(0, np.nan).fillna(mode_passenger)
        )

        # Impute trip_distance: replace 0 with mean of positive values
        mean_distance = df_clean[df_clean['trip_distance'] > 0]['trip_distance'].mean()
        df_clean['trip_distance'] = df_clean['trip_distance'].replace(0, mean_distance)

        # Remove negative fares/amounts
        df_clean = df_clean[(df_clean['fare_amount'] >= 0) & (df_clean['total_amount'] >= 0)]

        # Allow zero total_amount only for no-charge/dispute/voided payment types
        valid_zero_payment = [3, 4, 6]
        df_clean = df_clean[
            (df_clean['total_amount'] > 0) |
            (df_clean['payment_type'].isin(valid_zero_payment))
        ]

        # Filter to target year/month only (removes temporal anomalies)
        df_clean = df_clean[
            (df_clean['tpep_pickup_datetime'].dt.year == target_year) &
            (df_clean['tpep_pickup_datetime'].dt.month == target_month)
        ]

        rows_filtered = initial_rows - len(df_clean)
        logger.info(f"STEP [3/7]     : Cleaning complete.")
        logger.info(f"   >>> Total rows processed: {initial_rows}")
        logger.info(f"   >>> Anomaly rows removed: {rows_filtered}")
        logger.info(f"   >>> Clean rows remaining: {len(df_clean)}")

        # [4] Rename Columns
        df_clean.rename(
            columns={
                'tpep_pickup_datetime': 'pickup_datetime',
                'tpep_dropoff_datetime': 'dropoff_datetime',
                'passenger_count': 'total_passenger',
                'PULocationID': 'pickup_location',
                'DOLocationID': 'dropoff_location',
                'payment_type': 'payment_id',
            },
            inplace=True
        )
        logger.info("STEP [4/7]     : Columns renamed for Star Schema consistency.")

        # [5] Reorder Columns
        target_columns = [
            'pickup_location', 'dropoff_location', 'pickup_datetime', 'dropoff_datetime',
            'weather_key', 'payment_id', 'total_passenger', 'fare_amount', 'tip_amount',
            'total_amount', 'trip_distance'
        ]
        df_clean = df_clean.reindex(columns=target_columns)
        logger.info("STEP [5/7]     : Columns reordered to match Fact Table schema.")

        # [6] Build dim_datetime
        all_time = pd.concat(
            [df_clean['pickup_datetime'], df_clean['dropoff_datetime']],
            ignore_index=True
        )
        dim_datetime = pd.DataFrame({'date_key': all_time})

        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        dim_datetime['hour'] = dim_datetime['date_key'].dt.hour
        dim_datetime['day'] = dim_datetime['date_key'].dt.day
        dim_datetime['day_of_week'] = dim_datetime['date_key'].dt.weekday.map(day_map)
        dim_datetime['month'] = dim_datetime['date_key'].dt.month
        dim_datetime['year'] = dim_datetime['date_key'].dt.year

        dim_datetime['date_key'] = dim_datetime['date_key'].dt.strftime('%Y%m%d%H%M').astype('int64')
        dim_datetime.drop_duplicates(subset=['date_key'], keep='first', inplace=True)
        dim_datetime.reset_index(drop=True, inplace=True)

        logger.info(f"STEP [6/7]     : Created datetime dimension. Unique timestamps: {len(dim_datetime)}")

        # [7] Final Type Casting
        df_clean['total_passenger'] = df_clean['total_passenger'].astype(int)
        df_clean['weather_key'] = df_clean['pickup_datetime'].dt.strftime('%Y%m%d%H').astype('int64')
        df_clean['pickup_datetime'] = df_clean['pickup_datetime'].dt.strftime('%Y%m%d%H%M').astype('int64')
        df_clean['dropoff_datetime'] = df_clean['dropoff_datetime'].dt.strftime('%Y%m%d%H%M').astype('int64')

        logger.info("STEP [7/7]     : Final data types converted.")
        logger.info(f"TRANSFORM SUCCESS: {file_name} ready. Fact rows: {len(df_clean)}, Datetime rows: {len(dim_datetime)}")

        return dim_datetime, df_clean

    except Exception as e:
        logger.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None


def transform_weather(file_path: str):
    """Transform raw weather JSON into dim_weather DataFrame."""
    file_name = os.path.basename(file_path)

    logger.info(f"TRANSFORM START: Processing {file_name}")
    logger.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        with open(file_path, "r") as f:
            data = json.load(f)

        df_clean = pd.DataFrame(data['hourly'])
        logger.info(f"STEP [1/6]     : JSON data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Handle Null Values
        # PERBAIKAN: interpolate() dengan inplace=True mengembalikan None — harus di-assign
        null_count = df_clean.isnull().sum().sum()
        if null_count > 0:
            df_clean = df_clean.interpolate(method='linear', limit_direction='both', limit=2)
            df_clean = df_clean.fillna(0)
            logger.info(f"STEP [2/6]     : Imputed {null_count} null values using interpolation.")
        else:
            logger.info(f"STEP [2/6]     : No null values found.")

        # [3] Handle Duplicates
        # PERBAIKAN: drop_duplicates() dengan inplace=True mengembalikan None — harus di-assign
        dup_count = df_clean.duplicated().sum()
        if dup_count > 0:
            df_clean = df_clean.drop_duplicates(keep='first')
            logger.info(f"STEP [3/6]     : Removed {dup_count} duplicate rows.")
        else:
            logger.info(f"STEP [3/6]     : No duplicate rows found.")

        # [4] Datetime Conversion & Renaming
        df_clean['time'] = pd.to_datetime(df_clean['time'])
        df_clean.rename(
            columns={
                'time': 'full_time_stamp',
                'temperature_2m': 'temperature'
            },
            inplace=True
        )
        logger.info(f"STEP [4/6]     : Datetime converted and columns renamed.")

        # [5] Create Primary Key (YYYYMMDDHH)
        df_clean['weather_key'] = df_clean['full_time_stamp'].dt.strftime('%Y%m%d%H').astype(int)
        logger.info(f"STEP [5/6]     : Created weather_key from timestamp.")

        # [6] Reorder Columns
        target_columns = ['weather_key', 'full_time_stamp', 'temperature', 'precipitation', 'weather_code']
        df_clean = df_clean.reindex(columns=target_columns)
        logger.info(f"STEP [6/6]     : Columns reordered to match database schema.")

        logger.info(f"TRANSFORM SUCCESS: {file_name} is ready. Final rows: {len(df_clean)}")
        return df_clean

    except Exception as e:
        logger.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None
