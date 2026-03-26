import logging
import os
from datetime import datetime


os.makedirs('logs', exist_ok=True)

log_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    filename=os.path.join("logs", log_filename),
    level=logging.INFO, # Catat dari level INFO ke atas (WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)