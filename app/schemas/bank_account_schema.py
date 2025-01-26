from pydantic import BaseModel
from datetime import datetime


class BankAccountCreate(BaseModel):
    account_number: str
    balance: float
    account_type: str
    status: str
    owner_id: int

    class Config:
        from_attributes = True


class BankAccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    account_type: str
    status: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

