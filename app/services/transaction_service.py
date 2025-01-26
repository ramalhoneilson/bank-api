from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.bank_account import BankAccount
from app.models.transaction import Transaction, TransactionType
from app.utils.exceptions import InsufficientFundsError, AccountNotFoundError
from app.dao.transaction_dao import TransactionDAO
from app.services.bank_account_service import BankAccountService


class TransactionService:

    def __init__(self, bank_account_service: BankAccountService, transaction_dao: TransactionDAO):
        self.bank_account_service = bank_account_service
        self.transaction_dao = transaction_dao

    def create_deposit_transaction(
        self,
        db: Session,
        amount: Decimal,
        destination_account_id: int = None,
    ) -> Transaction:
        """
        Creates a deposit transaction with thread safety and validation logic.
        For deposits, the source account is the cash holding account (administrative_entity) and the destination account is the user account.
        """
        transaction_type = TransactionType.DEPOSIT
        # fixing this for the time being. Usually there are multiple cash holding accounts
        CASH_HOLDING_ACCOUNT_ID = 1 

        if not destination_account_id:
            raise ValueError("Destination account is required for deposits.")
        destination_account = self._get_and_lock_account(db, destination_account_id)
        if not destination_account:
            raise AccountNotFoundError("Destination account not found.")
        cash_holding_account = self._get_and_lock_administrative_account(db, CASH_HOLDING_ACCOUNT_ID)
        if not cash_holding_account:
            raise AccountNotFoundError("Cash Holding Account not found.")
        cash_holding_account.balance -= amount
        destination_account.balance += amount
        source_account_id = cash_holding_account.id

        transaction = Transaction(
            amount=amount,
            transaction_type=transaction_type,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction


    def create_transfer(
        self,
        db: Session,
        amount: Decimal,
        source_account_id: int = None,
        destination_account_id: int = None,
    ) -> Transaction:
        """
        Create a new transaction with thread safety and validation logic.
        """
        
        if not source_account_id or not destination_account_id:
            raise ValueError("Source and destination accounts are required for transfers.")
        
        source_account = self._get_and_lock_account(db, source_account_id)
        destination_account = self._get_and_lock_account(db, destination_account_id)
        if not source_account or not destination_account:
            raise AccountNotFoundError("One or both accounts not found.")
        
        if source_account.balance < amount:
            raise InsufficientFundsError("Insufficient funds in the source account.")
        
        source_account.balance -= amount
        destination_account.balance += amount

        transaction_type = TransactionType.TRANSFER
        # Create and save the transaction
        transaction = Transaction(
            amount=amount,
            transaction_type=transaction_type,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    def create_withdrawal(
        self,
        db: Session,
        amount: Decimal,
        source_account_id: int = None,
    ) -> Transaction:
        """
        Create a new transaction with thread safety and validation logic.
        """
        if not source_account_id:
            raise ValueError("Source account is required for withdrawals.")
        
        source_account = self._get_and_lock_account(db, source_account_id)
        if not source_account:
            raise AccountNotFoundError("Source account not found.")
        
        if source_account.balance < amount:
            raise InsufficientFundsError("Insufficient funds in the source account.")
        
        CASH_DISBURSEMENT_ACCOUNT_ID = 2
        
        cash_disbursement_account = self._get_and_lock_administrative_account(db, CASH_DISBURSEMENT_ACCOUNT_ID)
        if not cash_disbursement_account:
            raise AccountNotFoundError("Cash Disbursement Account not found.")
        
        source_account.balance -= amount
        cash_disbursement_account.balance += amount
        destination_account_id = cash_disbursement_account.id

        transaction_type = TransactionType.WITHDRAW
        transaction = Transaction(
            amount=amount,
            transaction_type=transaction_type,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction


    def _get_and_lock_account(self, db: Session, account_id: int) -> BankAccount:
        """
        Fetch and lock a bank account for thread safety.
        """
        return db.execute(
            select(BankAccount)
            .where(BankAccount.id == account_id)
            .with_for_update()
        ).scalar_one_or_none()

    def _get_and_lock_administrative_account(self, db: Session, administrative_account_id: int) -> BankAccount:
        """
        Fetch and lock an bank account associated with the administrative_account_id
        """
        return db.execute(
            select(BankAccount)
            .where(BankAccount.administrative_entity_id == administrative_account_id)
            .with_for_update()
        ).scalar_one_or_none()
  

    def create_deposit(self, db: Session, amount: Decimal, destination_account_id: int) -> Transaction:
        """
        Create a new deposit transaction.
        """
        return self.create_transaction(
            db,
            amount=amount,
            transaction_type=TransactionType.DEPOSIT,
            destination_account_id=destination_account_id,
        )

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> Transaction:
        """
        Fetch a transaction by its ID.
        """
        return self.transaction_dao.get_transaction_by_id(db, transaction_id)
