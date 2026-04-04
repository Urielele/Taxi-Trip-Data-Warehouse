from sqlalchemy import create_engine, text
import pandas as pd
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
    
    try:
        engine = create_engine(config.DATABASE_URL)
        
        if table_name.startswith('dim_'):
            key_column = 'date_key' if 'datetime' in table_name else 'weather_key'
            
            try:
                query = f"SELECT {key_column} FROM {table_name}"
                existing_ids = pd.read_sql(query, engine)[key_column].tolist()
                

                df_to_load = df[~df[key_column].isin(existing_ids)].copy()
                
                rows_skipped = len(df) - len(df_to_load)
                if rows_skipped > 0:
                    logging.info(f"SKIPPED: {rows_skipped} rows already exist in {table_name}.")
            
            except Exception as e:
                logging.warning(f"Could not check existing IDs for {table_name}, loading all data. Error: {e}")
                df_to_load = df
        
        else:
            df_to_load = df


        logging.info(f"ROWS TO LOAD : {len(df_to_load)}")
        
        if not df_to_load.empty:
            df_to_load.to_sql(
                table_name, 
                engine, 
                if_exists='append', 
                index=False,
                chunksize=100000,
                method='multi'
            )
            logging.info(f"LOAD SUCCESS: Data loaded into {table_name} successfully.")
        else:
            logging.info(f"LOAD SKIP: All data in {table_name} is already up to date.")
    
    except Exception as e:
        logging.error(f"LOAD FAILED : Could not load data into {table_name}. Details: {e}")