from pydantic import BaseModel
from app.models.bank_account import AccountType
from pydantic.dataclasses import ConfigDict

class BankAccountCreate(BaseModel):
    balance: float
    account_type: AccountType
    status: str
    owner_id: int

    model_config = ConfigDict(
        extra="forbid"
    )


class BankAccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    account_type: AccountType
    status: str

