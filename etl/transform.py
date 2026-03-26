import pandas as pd
import json
import os
import logging
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
    df_trip = pd.read_parquet("landing/yellow_tripdata_2023-01.parquet")
    print(df_trip.head(5))


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
            df_clean = df_clean.interpolate(method='linear', limit_direction='both', limit=2)
            df_clean = df_clean.fillna(0)

            logging.info(f"STEP [2/6]     : Imputed {null_count} null values using Interpolation.")

        else:
            logging.info(f"STEP [2/6]     : No null values found.")
 
        # [3] Handling Duplicates
        dup_count = df_clean.duplicated().sum()

        if dup_count > 0:
            df_clean = df_clean.drop_duplicates(keep='first')

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

