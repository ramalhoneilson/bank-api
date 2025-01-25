from fastapi import FastAPI
from app.controllers.account_controller import router as account_router
from app.controllers.customer_controller import router as customer_router
from app.database.session import engine
from app.database.base import Base
from app.models.account import Account  # noqa
from app.models.customer import Customer  # noqa


Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Banking App API",
    description="REST API for Bank Account Management",
    version="0.1.0"
)

# Include router
app.include_router(account_router, prefix="/api/v1", tags=["accounts"])
app.include_router(customer_router, prefix="/api/v1", tags=["customers"])


@app.get("/ping")
def health_check():
    return {"status": "ok"}
