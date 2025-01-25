from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str = Field(..., description="Customer name")

    class Config:
        from_attributes = True


class CustomerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
