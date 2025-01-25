from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class AccountCreate(BaseModel):
    customer_id: int
    initial_deposit: Decimal = Field(..., gt=0, description="Initial deposit amount")
    account_type: str = Field(..., description="Type of account")

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id: int
    account_number: str
    balance: Decimal
    account_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
