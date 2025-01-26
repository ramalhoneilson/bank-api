from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., description="Customer name")

    class Config:
        from_attributes = True


class CustomerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
