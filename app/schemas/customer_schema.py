from pydantic import BaseModel

# customer_name should be mandatory and a string type
class CustomerBase(BaseModel):
    customer_name: str


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    customer_name: str

