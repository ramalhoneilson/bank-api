from pydantic import BaseModel
from api.models.bank_account import AccountType
from pydantic.dataclasses import ConfigDict
from api.models.bank_account import AccountStatus

class BankAccountCreate(BaseModel):
    balance: float
    account_type: AccountType
    status: AccountStatus
    owner_id: int

    model_config = ConfigDict(
        extra="forbid"
    )


class BankAccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    account_type: AccountType
    status: AccountStatus

