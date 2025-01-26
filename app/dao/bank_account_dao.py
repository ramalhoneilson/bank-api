from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.bank_account import BankAccount
from app.schemas.bank_account_schema import BankAccountCreate
from app.models.bank_account import AccountType
import logging


logger = logging.getLogger(__name__)

class BankAccountDAO:

    def create_account(self, db: Session, account_data: BankAccountCreate) -> BankAccount:
        account_number = str(uuid.uuid4()).replace("-", "")[:12].upper()
        logger.info(f"AccountType: {account_data.account_type}")
        if account_data.account_type == AccountType.USER:            
            account_number = "C" + account_number
            db_account = BankAccount(
                customer_id=account_data.owner_id,
                administrative_entity_id = None,
                account_number=account_number,
                balance=account_data.balance,
                account_type=account_data.account_type,
            )
        elif account_data.account_type == AccountType.ADMINISTRATIVE:
            account_number = "A" + account_number
            db_account = BankAccount(
                customer_id=None,
                administrative_entity_id=account_data.owner_id,
                account_number=account_number,
                balance=account_data.balance,
                account_type=account_data.account_type,
            )
        else:
            raise ValueError("Invalid account type")

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
