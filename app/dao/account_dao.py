import uuid
from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account_schema import AccountCreate


class AccountDAO:
    def create_account(self, db: Session, account_data: AccountCreate) -> Account:
        account_number = str(uuid.uuid4()).replace("-", "")[:12].upper()

        db_account = Account(
            customer_id=account_data.customer_id,
            account_number=account_number,
            balance=account_data.initial_deposit,
            account_type=account_data.account_type,
        )

        db.add(db_account)
        db.commit()
        db.refresh(db_account)

        return db_account
