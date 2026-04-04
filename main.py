import etl.extract as ext
import etl.transform as trn
import etl.load as ld
import pandas as pd
import numpy as np
import gc

# Static data extraction and transformation #
# ext.extract_taxi_zone() 
# dim_location = trn.transform_location("landing/taxi_zone_lookup.csv")
# ld.load_to_db(dim_location, "dim_location")


# Dynamic data extraction, transformation and loading #
def auto_pipeline(year, start_month, end_month):
    # Loop through the specified months and perform ETL for each month
    for month in range(start_month, end_month + 1):

        # Extract data for the specified year and month
        ext.extract_trip_data(year, month)  
        ext.extract_weather_data(year, month)

        # Transform the extracted data 
        dim_weather = trn.transform_weather(f"landing/weather_{year}_{month:02d}.json")
        dim_datetime, fact_taxi_trip = trn.transform_trip_data(f"landing/yellow_tripdata_{year}-{month:02d}.parquet")

        # Load the transformed data into the database 
        ld.load_to_db(dim_weather, "dim_weather")
        del dim_weather
        gc.collect()

        ld.load_to_db(dim_datetime, "dim_datetime")
        del dim_datetime
        gc.collect()

        ld.load_to_db(fact_taxi_trip, "fact_taxi_trips")
        del fact_taxi_trip
        gc.collect()


if __name__ == "__main__":
    # Run the ETL pipeline for the year 2023 and months April to June
    auto_pipeline(2023, 5, 6)