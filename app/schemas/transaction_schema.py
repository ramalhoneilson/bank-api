from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TransactionBase(BaseModel):
    amount: float
    transaction_type: str
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    pass


class DepositCreate(BaseModel):
    amount: float
    account_id: int


class WithdrawCreate(BaseModel):
    amount: float
    account_id: int


class TransferCreate(BaseModel):
    amount: float
    source_account_id: int
    destination_account_id: int


class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
