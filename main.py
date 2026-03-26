import etl.extract as ext

# =-=-=-=-= EXTRACT =-=-=-=-= #

ext.extract_taxi_zone()  # Data statis: diimpor satu kali saat inisialisasi.

year = 2023     # Input tahun yang akan digunakan dalam pipeline ekstraksi.
for month in range(1,4):    # Interval bulan yang akan diekstrak. Contoh: 1 - 4 (Januari - April)
    ext.extract_trip_data(year, month)  
    ext.extract_weather_data(year, month)


# =-=-=-=-= TRANSFORM =-=-=-=-= #

