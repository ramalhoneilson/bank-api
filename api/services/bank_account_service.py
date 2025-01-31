from typing import List
from sqlalchemy.orm import Session
from api.dao.bank_account_dao import BankAccountDAO
from api.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse
from api.models.bank_account import BankAccount, AccountType
from sqlalchemy.orm import Session, attributes
from typing import Optional



class BankAccountService:
    def __init__(self, account_dao: BankAccountDAO):
        self.account_dao = account_dao

    def create_new_account(self, db: Session, account_data: BankAccountCreate) -> BankAccountResponse:
        created_account = self.account_dao.create_account(db, account_data)
        return BankAccountResponse.model_validate(attributes.instance_dict(created_account))

    def get_all_accounts(self, db: Session) -> List[BankAccountResponse]:
        accounts = self.account_dao.get_all_accounts(db)
        return [BankAccountResponse.model_validate(attributes.instance_dict(account)) for account in accounts] 

    def get_account_by_id(self, db: Session, account_id: int) -> Optional[BankAccountResponse]:
        account = self.account_dao.get_account_by_id(db, account_id)
        if account:
            return BankAccountResponse.model_validate(attributes.instance_dict(account))
        return None

    def get_administrative_account(self, db: Session, account_name: str) -> Optional[BankAccountResponse]:
        account = self.account_dao.get_account_by_name_and_type(db, account_name, AccountType.ADMINISTRATIVE)
        if account:
            return BankAccountResponse.model_validate(attributes.instance_dict(account))
        return None
