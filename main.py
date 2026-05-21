import gc
import etl.extract as ext
import etl.transform as trn
import etl.load as ld
from logger import logger


def load_static_data():
    """Extract dan load data statis (taxi zone) — jalankan sekali saja."""
    ext.extract_taxi_zone()
    dim_location = trn.transform_location("landing/taxi_zone_lookup.csv")
    ld.load_to_db(dim_location, "dim_location")


def auto_pipeline(year: int, start_month: int, end_month: int):
    """Jalankan ETL pipeline untuk rentang bulan yang ditentukan."""
    logger.info(f"PIPELINE START: year={year}, months={start_month}–{end_month}")

    for month in range(start_month, end_month + 1):
        logger.info(f"--- Processing {year}-{month:02d} ---")

        # Extract
        trip_ok = ext.extract_trip_data(year, month)
        weather_ok = ext.extract_weather_data(year, month)

        if not trip_ok or not weather_ok:
            logger.error(f"PIPELINE SKIP: Extract gagal untuk {year}-{month:02d}. Lanjut ke bulan berikutnya.")
            continue

        # Transform
        dim_weather = trn.transform_weather(f"landing/weather_{year}_{month:02d}.json")
        result = trn.transform_trip_data(f"landing/yellow_tripdata_{year}-{month:02d}.parquet")

        if result is None or dim_weather is None:
            logger.error(f"PIPELINE SKIP: Transform gagal untuk {year}-{month:02d}.")
            continue

        dim_datetime, fact_taxi_trip = result

        # Load — urutan penting: dimensi dulu sebelum fakta (FK constraint)
        ld.load_to_db(dim_weather, "dim_weather")
        del dim_weather
        gc.collect()

        ld.load_to_db(dim_datetime, "dim_datetime")
        del dim_datetime
        gc.collect()

        ld.load_to_db(fact_taxi_trip, "fact_taxi_trips")
        del fact_taxi_trip
        gc.collect()

        logger.info(f"--- {year}-{month:02d} DONE ---")

    logger.info("PIPELINE COMPLETE.")


if __name__ == "__main__":
    # Uncomment baris di bawah untuk load data statis (jalankan sekali saja)
    # load_static_data()

    # Jalankan pipeline untuk April–Juni 2023
    auto_pipeline(2023, 4, 6)
