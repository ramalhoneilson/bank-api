from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.bank_account import BankAccount
from app.schemas.bank_account_schema import BankAccountCreate


class BankAccountDAO:

    def create_account(self, db: Session, account_data: BankAccountCreate) -> BankAccount:
        account_number = str(uuid.uuid4()).replace("-", "")[:12].upper()

        db_account = BankAccount(
            customer_id=account_data.customer_id,
            account_number=account_number,
            balance=account_data.initial_deposit,
            account_type=account_data.account_type,
        )

        db.add(db_account)
        db.commit()
        db.refresh(db_account)

        return db_account

    def get_account_by_id(self, db: Session, account_id: int) -> Optional[BankAccount]:
        """
        Fetch an account by its ID.
        """
        return db.query(BankAccount).filter(BankAccount.id == account_id).first()

    def get_all_accounts(self, db: Session) -> List[BankAccount]:
        """
        Fetch all accounts.
        """
        return db.query(BankAccount).all()
