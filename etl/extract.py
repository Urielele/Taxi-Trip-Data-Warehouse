import os
import requests
import pandas as pd
import calendar
import shutil

# Gunakan shared logger — tidak perlu setup ulang di sini
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger


def archive_to_raw(source_path: str, category: str, year: int, month: int):
    target_dir = f"raw/{category}/{year}/{month}"
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, os.path.basename(source_path))

    try:
        shutil.copy2(source_path, target_path)
        logger.info(f"ARCHIVE SUCCESS: {os.path.basename(source_path)}")
        logger.info(f"DESTINATION    : {target_path}")

    except Exception as e:
        logger.error(f"ARCHIVE FAILED : Could not copy {source_path}. Details: {e}")


def extract_taxi_zone():
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
    save_path = "landing/taxi_zone_lookup.csv"

    try:
        logger.info(f"EXTRACT START: Fetching Taxi Zone Lookup")
        logger.info(f"SOURCE URL   : {url}")

        df = pd.read_csv(url)
        df.to_csv(save_path, index=False)

        archive_to_raw(save_path, "Taxi Zone", 0, 0)
        logger.info(f"SUCCESS      : Saved to {save_path}")
        return True

    except Exception as e:
        logger.error(f"FAILED       : Could not extract Taxi Zone. Details: {e}")
        return False


def extract_trip_data(year: int, month: int):
    file_name = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file_name}"
    save_path = f"landing/{file_name}"

    logger.info(f"EXTRACT START: Downloading {file_name}")
    logger.info(f"SOURCE URL   : {url}")

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        archive_to_raw(save_path, "Trip Records", year, month)
        logger.info(f"SUCCESS      : {file_name} saved to {save_path}")
        return True

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP FAILED  : File not found or server down for {file_name}. Details: {e}")
    except Exception as e:
        logger.error(f"UNEXPECTED FAILURE: {e}")

    return False


def extract_weather_data(year: int, month: int):
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    file_name = f"weather_{year}_{month:02d}.json"
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude=40.71&longitude=-74"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,precipitation,weather_code"
    )
    save_path = f"landing/{file_name}"

    logger.info(f"EXTRACT START: Downloading {file_name}")
    logger.info(f"SOURCE URL   : {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        archive_to_raw(save_path, "Weather", year, month)
        logger.info(f"SUCCESS      : {file_name} saved to {save_path}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP FAILED  : File not found or server down for {file_name}. Details: {e}")
    except Exception as e:
        logger.error(f"UNEXPECTED FAILURE: {e}")

    return False
