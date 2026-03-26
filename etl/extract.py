import os
import requests
import pandas as pd
import logging
import calendar
import shutil
from datetime import datetime

os.makedirs('logs', exist_ok=True)

log_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    filename=os.path.join("logs", log_filename),
    level=logging.INFO, # Catat dari level INFO ke atas (WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def archive_to_raw(source_path: str, category: str, year: int, month: int):
    target_dir = f"raw/{category}/{year}/{month}"
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, os.path.basename(source_path))

    try:
        shutil.copy2(source_path, target_path)

        logging.info(f"ARCHIVE SUCCESS: {os.path.basename(source_path)}")
        logging.info(f"DESTINATION    : {target_path}")

    except Exception as e:
        logging.error(f"ARCHIVE FAILED : Could not copy {source_path}. Details: {e}")


def extract_taxi_zone():
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
    save_path = "landing/taxi_zone_lookup.csv"

    try:
        logging.info(f"EXTRACT START: Fetching Taxi Zone Lookup")
        logging.info(f"SOURCE URL   : {url}")

        df = pd.read_csv(url)
        df.to_csv(save_path, index=False)

        archive_to_raw(save_path, "Taxi Zone", 0, 0)
        logging.info(f"SUCCESS      : Saved to {save_path}")
        return True
    
    except Exception as e:
        logging.error(f"FAILED       : Could not extract Taxi Zone. Details: {e}")
        return False


def extract_trip_data(year: int, month: int):
    file_name = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file_name}"
    save_path = f"landing/{file_name}"

    logging.info(f"EXTRACT START: Downloading {file_name}")
    logging.info(f"SOURCE URL   : {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        archive_to_raw(save_path, "Trip Records", year, month)
        logging.info(f"SUCCESS      : {file_name} saved to {save_path}")
        return True

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP FAILED  : File not found or server down for {file_name}. Details: {e}")
    except Exception as e:
        logging.error(f"UNEXPECTED FAILURE: {e}")
    
    return False


def extract_weather_data(year: int, month:int):
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    file_name = f"weather_{year}_{month:02d}.json"
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=40.71&longitude=-74&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,precipitation,weather_code"
    save_path = f"landing/{file_name}"

    logging.info(f"EXTRACT START: Downloading {file_name}")
    logging.info(f"SOURCE URL   : {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        archive_to_raw(save_path, "Weather", year, month)
        logging.info(f"SUCCESS      : {file_name} saved to {save_path}")
        return True
    
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP FAILED  : File not found or server down for {file_name}. Details: {e}")
    except Exception as e:
        logging.error(f"UNEXPECTED FAILURE: {e}")

    return False

