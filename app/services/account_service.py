from sqlalchemy.orm import Session
from app.dao.account_dao import AccountDAO
from app.schemas.account_schema import AccountCreate, AccountResponse


class AccountService:
    def __init__(self, account_dao: AccountDAO):
        self.account_dao = account_dao

    def create_new_account(
        self, db: Session, account_data: AccountCreate
    ) -> AccountResponse:
        # TODO: validation

        created_account = self.account_dao.create_account(db, account_data)

        return AccountResponse.from_orm(created_account)
