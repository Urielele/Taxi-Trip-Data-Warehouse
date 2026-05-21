import logging
import os
from datetime import datetime

os.makedirs('logs', exist_ok=True)

log_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.log"

# Gunakan named logger agar tidak konflik dengan root logger
logger = logging.getLogger("taxi_etl")

# Cegah handler bertumpuk jika modul di-import ulang
if not logger.handlers:
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        os.path.join("logs", log_filename),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
