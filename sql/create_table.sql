CREATE TABLE dim_location (
  location_id INT,
  borough VARCHAR,
  zone VARCHAR,
  PRIMARY KEY (location_id)
);


CREATE TYPE DOW AS ENUM ('sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat');
CREATE TABLE dim_datetime (
  date_key INT,
  hour INT,
  day INT,
  day_of_week DOW,
  month INT,
  year SMALLINT,
  PRIMARY KEY (date_key),
  CONSTRAINT hour_check CHECK (hour BETWEEN 0 AND 23),
  CONSTRAINT day_check CHECK (day BETWEEN 1 AND 31),
  CONSTRAINT month_check CHECK (month BETWEEN 1 AND 12)
);


CREATE TABLE dim_weather (
  weather_key INT,
  full_time_stamp TIMESTAMP,
  day INT,
  hour INT,
  weather_code INT,
  temperature DECIMAL,
  precipitation DECIMAL,
  PRIMARY KEY (weather_key),
  CONSTRAINT day_check CHECK (day BETWEEN 1 AND 31),
  CONSTRAINT hour_check CHECK (hour BETWEEN 1 AND 31)
);


CREATE TABLE dim_payment (
  payment_id INT,
  payment_name VARCHAR,
  PRIMARY KEY (payment_id)
);


CREATE TABLE fact_taxi_trips (
  pickup_location INT,
  dropoff_location INT,
  pickup_datetime INT,
  dropoff_datetime INT,
  weather_key INT,
  payment_id INT,
  total_passenger INT,
  fare_amount DECIMAL,
  tip_amount DECIMAL,
  total_amount DECIMAL,
  trip_distance DECIMAL,
  
  CONSTRAINT fk_pul 
  	FOREIGN KEY (pickup_location)
  		REFERENCES dim_location (location_id)
			ON DELETE RESTRICT ON UPDATE CASCADE,
  
  CONSTRAINT fk_dol
  	FOREIGN KEY (dropoff_location)
  		REFERENCES dim_location (location_id)
  			ON DELETE RESTRICT ON UPDATE CASCADE,
 
  constraint fk_put
  	FOREIGN KEY (pickup_datetime)
  		REFERENCES dim_datetime (date_key)
  			ON DELETE RESTRICT ON UPDATE CASCADE,
  
  CONSTRAINT fk_dot
  	FOREIGN KEY (dropoff_datetime)
  		REFERENCES dim_datetime (date_key)
  			ON DELETE RESTRICT ON UPDATE CASCADE,
  
  CONSTRAINT fk_weather
  	FOREIGN KEY (weather_key)
  		REFERENCES dim_weather (weather_key)
  			ON DELETE RESTRICT ON UPDATE CASCADE,
  
  CONSTRAINT fk_payment
  	FOREIGN KEY (payment_id)
  		REFERENCES dim_payment (payment_id)
  			ON DELETE RESTRICT ON UPDATE CASCADE
);