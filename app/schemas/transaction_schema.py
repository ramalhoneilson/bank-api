from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.models.transaction import TransactionType
from pydantic.dataclasses import ConfigDict


class TransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
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

    model_config = ConfigDict(
        extra="forbid"
    )
