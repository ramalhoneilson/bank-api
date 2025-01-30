from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Enum
from datetime import datetime
from datetime import timezone
from enum import Enum as PythonEnum
from api.database.base import Base

class TransactionType(PythonEnum):
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    transaction_type = Column(Enum(TransactionType), nullable=False)
    source_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
    destination_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
