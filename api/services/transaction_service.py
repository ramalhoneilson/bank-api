from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from api.models.bank_account import BankAccount
from api.models.transaction import Transaction, TransactionType
from api.schemas.transaction_schema import TransactionResponse
from api.utils.exceptions import InsufficientFundsError, AccountNotFoundError
from api.dao.transaction_dao import TransactionDAO
from api.services.bank_account_service import BankAccountService
import logging
from api.config.config import CASH_HOLDING_ACCOUNT_ID, CASH_DISBURSEMENT_ACCOUNT_ID

logger = logging.getLogger(__name__)


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
        try:
            if not destination_account_id:
                raise ValueError("Destination account is required for deposits.")
            
            logger.info(f"Processing deposit: {amount} to account: {destination_account_id}")
            
            amount_decimal = Decimal(str(amount))
            
            if amount_decimal <= 0:
                raise ValueError("Amount must be positive.")

            destination_account = self._get_and_lock_account(db, destination_account_id)
            if not destination_account:
                raise AccountNotFoundError("Destination account not found.")
            logger.info(f"Destination account found: {destination_account.id}")

            cash_holding_account = self._get_and_lock_account(db, CASH_HOLDING_ACCOUNT_ID)
            if not cash_holding_account:
                raise AccountNotFoundError("Cash Holding Account not found.")
            logger.info(f"Cash holding account found: {cash_holding_account.id}")

            cash_holding_account.balance -= amount_decimal
            destination_account.balance += amount_decimal

            transaction = Transaction(
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                source_account_id=cash_holding_account.id,
                destination_account_id=destination_account_id,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Deposit transaction created: {transaction.id}")
            return transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error during deposit transaction: {e}")
            raise e

    def create_transfer(
        self,
        db: Session,
        amount: Decimal,
        source_account_id: int = None,
        destination_account_id: int = None,
    ) -> Transaction:
        """
        Create a new transfer transaction with thread safety and validation logic.
        """
        try:
            if not source_account_id or not destination_account_id:
                raise ValueError("Source and destination accounts are required for transfers.")

            amount_decimal = Decimal(str(amount))

            if amount_decimal <= 0:
                raise ValueError("Amount must be positive.")

            source_account = self._get_and_lock_account(db, source_account_id)
            destination_account = self._get_and_lock_account(db, destination_account_id)
            if not source_account or not destination_account:
                raise AccountNotFoundError("One or both accounts not found.")

            if source_account.balance < amount_decimal:
                raise InsufficientFundsError("Insufficient funds in the source account.")

            source_account.balance -= amount_decimal
            destination_account.balance += amount_decimal

            transaction = Transaction(
                amount=amount_decimal,
                transaction_type=TransactionType.TRANSFER,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Transfer transaction created: {transaction.id}")
            return transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error during transfer transaction: {e}")
            raise e

    def create_withdrawal(
        self,
        db: Session,
        amount: Decimal,
        source_account_id: int = None,
    ) -> Transaction:
        """
        Create a new withdrawal transaction with thread safety and validation logic.
        """
        try:
            if not source_account_id:
                raise ValueError("Source account is required for withdrawals.")
            
            amount_decimal = Decimal(str(amount))

            if amount_decimal <= 0:
                raise ValueError("Amount must be positive.")

            source_account = self._get_and_lock_account(db, source_account_id)
            if not source_account:
                raise AccountNotFoundError("Source account not found.")

            if source_account.balance < amount_decimal:
                raise InsufficientFundsError("Insufficient funds in the source account.")

            cash_disbursement_account = self._get_and_lock_account(db, CASH_DISBURSEMENT_ACCOUNT_ID)
            if not cash_disbursement_account:
                raise AccountNotFoundError("Cash Disbursement Account not found.")

            source_account.balance -= amount_decimal
            cash_disbursement_account.balance += amount_decimal

            transaction = Transaction(
                amount=amount_decimal,
                transaction_type=TransactionType.WITHDRAW,
                source_account_id=source_account_id,
                destination_account_id=cash_disbursement_account.id,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Withdrawal transaction created: {transaction.id}")
            return transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error during withdrawal transaction: {e}")
            raise e

    def _get_and_lock_account(self, db: Session, account_id: int) -> BankAccount:
        """
        Fetch and lock a bank account for thread safety.
        """
        return db.execute(
            select(BankAccount)
            .where(BankAccount.id == account_id)
            .with_for_update()
        ).scalar_one_or_none()

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> Transaction:
        """
        Fetch a transaction by its ID.
        """
        return self.transaction_dao.get_transaction_by_id(db, transaction_id)

    def list_transactions(self, db: Session, account_id: int) -> List[TransactionResponse]:
        account = self.account_dao.get_account_by_id(db, account_id)
        transactions = account.transactions
        return [TransactionResponse.model_validate(transaction) for transaction in transactions]
