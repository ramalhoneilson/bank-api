from pydantic import BaseModel


class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float

    class Config:
        from_attributes = True


class TransferResponse(BaseModel):
    id: int
    from_account_id: str
    to_account_id: int

    class Config:
        from_attributes = True
