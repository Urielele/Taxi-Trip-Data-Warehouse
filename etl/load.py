from sqlalchemy import create_engine
import logging
import os
from config import config
from datetime import datetime

os.makedirs('logs', exist_ok=True)

log_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    filename=os.path.join("logs", log_filename),
    level=logging.INFO, # Catat dari level INFO ke atas (WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def load_to_db(df, table_name):
    logging.info(f"LOAD START: Loading data into {table_name} table.")
    logging.info(f"ROWS TO LOAD : {len(df)}")

    try:
        engine = create_engine(config.DATABASE_URL)
        df.to_sql(
            table_name, 
            engine, 
            if_exists='append', 
            index=False,
            chunksize=100000,
            method='multi'
            )

        logging.info(f"LOAD SUCCESS: Data loaded into {table_name} successfully.")
    
    except Exception as e:
        logging.error(f"LOAD FAILED : Could not load data into {table_name}. Details: {e}")