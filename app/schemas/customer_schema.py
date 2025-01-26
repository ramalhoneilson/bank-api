from pydantic import BaseModel


class CustomerBase(BaseModel):
    customer_name: str


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True
