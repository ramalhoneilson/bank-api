from pydantic import BaseModel
from app.models.bank_account import AccountType

class BankAccountCreate(BaseModel):
    balance: float
    account_type: AccountType
    status: str
    owner_id: int

    class Config:
        from_attributes = True


class BankAccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    account_type: AccountType
    status: str

    class Config:
        from_attributes = True

