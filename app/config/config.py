import os
from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
# dev, qa, test or prod
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
# if dev, we use sqlite
if ENVIRONMENT == "dev":
    DATABASE_URL = "sqlite:///./test.db"    
else:
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
print(f"Connecting to database: {DATABASE_URL}")
logger.info(f"Connecting to database: {DATABASE_URL}")

DEBUG = os.getenv("DEBUG", "False") == "True"
