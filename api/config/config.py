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
if ENVIRONMENT == "local":
    DATABASE_URL = "sqlite:///:memory:"
elif ENVIRONMENT == "test":
    DATABASE_URL = "sqlite:///./test.db"
else:
    # integration, qa, prod
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
print(f"DB URL: {DATABASE_URL}")

DEBUG = os.getenv("DEBUG", "False") == "True"


# I am keeping these as environment variables just to simplify the service.
# In a real-world scenario, these would be configured in the database.
CASH_HOLDING_ACCOUNT_ID = int(os.getenv('CASH_HOLDING_ACCOUNT_ID', '999999999999'))
CASH_DISBURSEMENT_ACCOUNT_ID = int(os.getenv('CASH_DISBURSEMENT_ACCOUNT_ID', '999999999998'))
