import pandas as pd
import numpy as np
import json
import os
import logging
import re
from datetime import datetime


os.makedirs('logs', exist_ok=True)

log_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    filename=os.path.join("logs", log_filename),
    level=logging.INFO, # Catat dari level INFO ke atas (WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def transform_zone(file_path: str):
    file_name = os.path.basename(file_path)

    logging.info(f"TRANSFORM START: Processing {file_name}")
    logging.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        df_clean = pd.read_csv(file_path)

        logging.info(f"STEP [1/4]     : CSV data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Drop Irrelevant Column
        df_clean.drop(columns=['service_zone'], inplace=True)

        logging.info(f"STEP [2/4]     : Drop 'service_zone' column.")

        # [3] Text Standardization
        df_clean['Borough'] = df_clean['Borough'].str.strip().str.title()
        df_clean['Zone'] = df_clean['Zone'].str.strip().str.title()

        logging.info(f"STEP [3/4]     : Standardized 'Borough' and 'Zone' (Strip & Title Case).")

        # [4] Renaming
        df_clean.rename(
            columns={
                'LocationID' : 'location_id', 
                'Borough' : 'borough', 
                'Zone' : 'zone'
            }, 
            inplace=True
        )

        logging.info(f"STEP [4/4]     : Renamed columns to match database schema.")

        logging.info(f"TRANSFORM SUCCESS: {file_name} is ready. Final rows: {len(df_clean)}")
        return df_clean
    
    except Exception as e:
        logging.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None


def transform_trip_data(file_path: str):
    
    file_name = os.path.basename(file_path)

    file_info = re.search(r'(\d{4})-(\d{2})', file_name)
    target_year = int(file_info.group(1))
    target_month = int(file_info.group(2))

    print(target_year)
    print(target_month)

    logging.info(f"TRANSFORM START: Processing {file_name}")
    logging.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        df_clean = pd.read_parquet(file_path)

        logging.info(f"STEP [1/6]     : CSV data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Drop Irrelevant Column
        df_clean.drop(columns=[
            'VendorID',
            'RatecodeID',
            'store_and_fwd_flag',
            'extra',
            'mta_tax',
            'tolls_amount',
            'improvement_surcharge',
            'congestion_surcharge',
            'airport_fee'
            ],
            inplace=True
        )

        logging.info(f"STEP [2/n]     : Drop 'VendorID', 'RatecodeID', 'store_and_fwd_flag', 'extra', 'mta_tax', 'tolls_amount', 'improvement_surcharge', 'congestion_surcharge', 'airport_fee' column.")

        # [3] Valdation Data

        mode_passenger = df_clean['passenger_count'].mode()[0]
        df_clean['passenger_count'] = df_clean['passenger_count'].replace(0, np.nan).fillna(mode_passenger)

        mean_distance = df_clean[df_clean['trip_distance'] > 0]['trip_distance'].mean()
        df_clean['trip_distance'] = df_clean['trip_distance'].replace(0, mean_distance)

        df_clean = df_clean[(df_clean['fare_amount'] > 0) & (df_clean['total_amount'] > 0)]

        df_clean = df_clean[
            (df_clean['tpep_pickup_datetime'].dt.year == target_year) & 
            (df_clean['tpep_pickup_datetime'].dt.month == target_month)
            ]
        
        # [4] Renaming & Reorder Column

        print(df_clean['passenger_count'].dtype)
        
        print(df_clean['passenger_count'].dtype)

        df_clean.rename(
            columns={
                'tpep_pickup_datetime' : 'pickup_datetime',
                'tpep_dropoff_datetime' : 'dropoff_datetime',
                'passenger_count' : 'total_passenger',
                'PULocationID' : 'pickup_location',
                'DOLocationID' : 'dropoff_location',
                'payment_type' : 'payment_id',
            },
            inplace=True
        )

        # [5] Reorder Columns

        target_columns = ['pickup_location', 'dropoff_location', 'pickup_datetime', 'dropoff_datetime', 
                         'weather_key', 'payment_id', 'total_passenger', 'fare_amount', 'tip_amount', 'total_amount', 'trip_distance']
        df_clean = df_clean.reindex(columns=target_columns)

        # [6] Make dim_datetime

        all_time = pd.concat([df_clean['pickup_datetime'], df_clean['dropoff_datetime']])

        dim_datetime = pd.DataFrame(all_time, columns=['date_key']).drop_duplicates().reset_index(drop=True)

        dim_datetime = dim_datetime.sort_values(by='date_key').reset_index(drop=True)

        dim_datetime['hour'] = dim_datetime['date_key'].dt.hour
        dim_datetime['day'] = dim_datetime['date_key'].dt.day
        dim_datetime['day_of_week'] = dim_datetime['date_key'].dt.weekday
        dim_datetime['month'] = dim_datetime['date_key'].dt.month
        dim_datetime['year'] = dim_datetime['date_key'].dt.year

        dim_datetime['date_key'] = dim_datetime['date_key'].dt.strftime('%Y%m%d%H%M').astype(int)

        # [7] Casting or wtv

        df_clean['total_passenger'] = df_clean['total_passenger'].astype(int)

        df_clean['weather_key'] = df_clean['pickup_datetime'].dt.strftime('%Y%m%d').astype(int)

        df_clean['pickup_datetime'] = df_clean['pickup_datetime'].dt.strftime('%Y%m%d%H%M').astype(int)
        df_clean['dropoff_datetime'] = df_clean['dropoff_datetime'].dt.strftime('%Y%m%d%H%M').astype(int)


        return df_clean, dim_datetime
    
    except Exception as e:
        logging.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None


def transform_weather(file_path: str):
    file_name = os.path.basename(file_path)

    logging.info(f"TRANSFORM START: Processing {file_name}")
    logging.info(f"FILE PATH      : {file_path}")

    try:
        # [1] Load Data
        with open(file_path, "r") as f:
            data = json.load(f)

        df_clean = pd.DataFrame(data['hourly'])

        logging.info(f"STEP [1/6]     : JSON data loaded into DataFrame. Rows: {len(df_clean)}")

        # [2] Handling Null Values
        null_count = df_clean.isnull().sum().sum()

        if null_count > 0:
            df_clean = df_clean.interpolate(method='linear', limit_direction='both', limit=2, inplace=True)
            df_clean = df_clean.fillna(0)

            logging.info(f"STEP [2/6]     : Imputed {null_count} null values using Interpolation.")

        else:
            logging.info(f"STEP [2/6]     : No null values found.")
 
        # [3] Handling Duplicates
        dup_count = df_clean.duplicated().sum()

        if dup_count > 0:
            df_clean = df_clean.drop_duplicates(keep='first', inplace=True)

            logging.info(f"STEP [3/6]     : Removed {dup_count} duplicate rows.")

        else:
            logging.info(f"STEP [3/6]     : No duplicate rows found.")
        
        # [4] Datetime Conversion & Renaming
        df_clean['time'] = pd.to_datetime(df_clean['time'])
        
        df_clean.rename(
            columns={
                'time': 'full_time_stamp',
                'temperature_2m': 'temperature'
            },
            inplace=True
        )

        logging.info(f"STEP [4/6]     : Datetime converted and columns renamed.")

        # [5] Create Primary Key (YYYYMMDDHH)
        df_clean['weather_key'] = df_clean['full_time_stamp'].dt.strftime('%Y%m%d%H').astype(int)

        logging.info(f"STEP [5/6]     : Created weather_key from timestamp.")

        # [6] Reorder Columns
        target_columns = ['weather_key', 'full_time_stamp', 'temperature', 'precipitation', 'weather_code']
        df_clean = df_clean.reindex(columns=target_columns)
        
        logging.info(f"STEP [6/6]     : Columns reordered to match Database Schema.")

        logging.info(f"TRANSFORM SUCCESS: {file_name} is ready. Final rows: {len(df_clean)}")
        return df_clean
    
    except Exception as e:
        logging.error(f"TRANSFORM FAILED : Error processing {file_name}. Details: {e}")
        return None


# transform_trip_data("landing/yellow_tripdata_2023-01.parquet")
# transform_zone("landing/taxi_zone_lookup.csv")
# dim_weather = transform_weather("landing/weather_2023_01.json")
# print(dim_weather.head(5))