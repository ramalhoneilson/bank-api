from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from api.models.transaction import TransactionType
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
    source_account_id: int


class WithdrawCreate(BaseModel):
    amount: float
    account_id: int


class TransferCreate(BaseModel):
    amount: float
    source_account_id: int
    destination_account_id: int


class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    source_account_id: Optional[int]
    destination_account_id: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_transaction(cls, transaction):
        return cls(
            id=transaction.id,
            amount=float(transaction.amount),
            transaction_type=transaction.transaction_type.value,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            timestamp=transaction.timestamp
        )
