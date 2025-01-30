import logging
from fastapi import FastAPI
from api.controllers.bank_account_controller import router as account_router
from api.controllers.customer_controller import router as customer_router
from api.controllers.transaction_controller import router as transaction_router
from api.controllers.administrative_entity_controller import router as administrative_entity_router
from api.database.session import engine
from api.database.base import Base
from api.models.bank_account import BankAccount  # noqa
from api.models.customer import Customer  # noqa

logger = logging.getLogger(__name__)


logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully.")

api = FastAPI(
    title="Banking App API",
    description="REST API for Bank Account Management",
    version="0.1.0",
)

api.include_router(account_router, prefix="/api/v1", tags=["bank-accounts"])
api.include_router(customer_router, prefix="/api/v1", tags=["customers"])
api.include_router(administrative_entity_router, prefix="/api/v1", tags=["administrative-entities"])
api.include_router(transaction_router, prefix="/api/v1", tags=["transactions"])


@api.get("/ping")
def health_check():
    return {"status": "ok"}
