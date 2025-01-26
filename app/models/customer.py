from sqlalchemy import Column, Integer, String
from app.database.base import Base
from sqlalchemy.orm import relationship


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    bank_accounts = relationship("BankAccount", back_populates="customer")
