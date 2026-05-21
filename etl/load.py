import pandas as pd
import os
from sqlalchemy import create_engine, text

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
from logger import logger

# Buat engine sekali di module level — tidak perlu dibuat ulang setiap pemanggilan
_engine = None


def get_engine():
    """Lazy singleton untuk SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            config.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True  # Cek koneksi sebelum dipakai
        )
    return _engine


# Mapping tabel ke primary key-nya
_TABLE_PK = {
    "dim_location": "location_id",
    "dim_datetime": "date_key",
    "dim_weather": "weather_key",
    "dim_payment": "payment_id",
}


def load_to_db(df: pd.DataFrame, table_name: str) -> bool:
    """
    Load DataFrame ke PostgreSQL.
    - Untuk tabel dimensi: skip baris yang sudah ada (upsert-safe via ON CONFLICT DO NOTHING).
    - Untuk tabel fakta: append langsung.
    """
    if df is None or df.empty:
        logger.warning(f"LOAD SKIP: DataFrame untuk {table_name} kosong atau None.")
        return False

    logger.info(f"LOAD START: Loading {len(df)} rows into '{table_name}'.")

    try:
        engine = get_engine()

        if table_name in _TABLE_PK:
            # Dimensi — gunakan ON CONFLICT DO NOTHING agar tidak duplikat
            # tanpa harus menarik semua existing IDs ke memori
            key_col = _TABLE_PK[table_name]
            _upsert_dimension(df, table_name, key_col, engine)
        else:
            # Fakta — langsung append
            df.to_sql(
                table_name,
                engine,
                if_exists='append',
                index=False,
                chunksize=50000,
                method='multi'
            )
            logger.info(f"LOAD SUCCESS: {len(df)} rows appended to '{table_name}'.")

        return True

    except Exception as e:
        logger.error(f"LOAD FAILED : Could not load data into '{table_name}'. Details: {e}")
        return False


def _upsert_dimension(df: pd.DataFrame, table_name: str, key_col: str, engine):
    """
    Insert baris baru ke tabel dimensi, skip jika primary key sudah ada.
    Menggunakan INSERT ... ON CONFLICT DO NOTHING — lebih efisien daripada
    menarik semua existing IDs ke memori Python.
    """
    cols = ", ".join(df.columns)
    placeholders = ", ".join([f":{c}" for c in df.columns])
    sql = text(
        f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders}) "
        f"ON CONFLICT ({key_col}) DO NOTHING"
    )

    records = df.to_dict(orient='records')
    inserted = 0
    skipped = 0

    with engine.begin() as conn:
        for i in range(0, len(records), 10000):
            batch = records[i:i + 10000]
            result = conn.execute(sql, batch)
            inserted += result.rowcount
            skipped += len(batch) - result.rowcount

    logger.info(f"LOAD SUCCESS: '{table_name}' — {inserted} inserted, {skipped} skipped (already exist).")
