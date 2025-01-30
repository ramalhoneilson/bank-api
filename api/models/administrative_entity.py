from sqlalchemy import Column, Integer, String

from api.database.base import Base
from sqlalchemy.orm import relationship


class AdministrativeEntity(Base):
    __tablename__ = 'administrative_entities'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tax_id = Column(String, nullable=False)
    coorporate_name = Column(String, nullable=False)

    bank_accounts = relationship("BankAccount", back_populates="administrative_entity")
