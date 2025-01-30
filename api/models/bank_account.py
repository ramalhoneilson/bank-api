from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from datetime import datetime
from enum import Enum as PythonEnum
from api.database.base import Base
from sqlalchemy.orm import relationship


class AccountType(PythonEnum):
    USER = "USER"
    ADMINISTRATIVE = "ADMINISTRATIVE"

class AccountStatus(PythonEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"



class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_number = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(10, 2), default=0.00)
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.USER)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    administrative_entity_id = Column(Integer, ForeignKey("administrative_entities.id"), nullable=True)

    customer = relationship("Customer", back_populates="bank_accounts")
    administrative_entity = relationship("AdministrativeEntity", back_populates="bank_accounts")
