from typing import List
from sqlalchemy.orm import Session
from app.dao.bank_account_dao import BankAccountDAO
from app.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse
from app.models.bank_account import BankAccount, AccountType


class BankAccountService:
    def __init__(self, account_dao: BankAccountDAO):
        self.account_dao = account_dao

    def create_new_account(self, db: Session, account_data: BankAccountCreate) -> BankAccountResponse:
        # TODO: validation

        created_account = self.account_dao.create_account(db, account_data)

        return BankAccountResponse.model_validate(created_account)
    
    def get_administrative_account(self, db: Session, account_name: str) -> BankAccount:
        """
        Get the only administrative account by name. We could have more depending on the requirements. 
        For instance, at Wirecard we have more than one administrative account for reporting purposes.
        """
        return self.account_dao.get_account_by_name_and_type(
            db, account_name, AccountType.ADMINISTRATIVE
        )
    
    def get_all_accounts(self, db: Session) -> List[BankAccountResponse]:
        accounts = self.account_dao.get_all_accounts(db)
        return [BankAccountResponse.model_validate(account) for account in accounts]
    
    def get_account_by_id(self, db: Session, account_id: int) -> BankAccountResponse:
        account = self.account_dao.get_account_by_id(db, account_id)
        return BankAccountResponse.model_validate(account)
    

