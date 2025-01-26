from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.bank_account import BankAccount, AccountType
from app.models.transaction import Transaction, TransactionType
from app.utils.exceptions import InsufficientFundsError, AccountNotFoundError


class TransactionService:
    def __init__(self, account_service, transaction_dao):
        self.account_service = account_service
        self.transaction_dao = transaction_dao

    def create_transaction(
        self,
        db: Session,
        amount: Decimal,
        transaction_type: TransactionType,
        source_account_id: int = None,
        destination_account_id: int = None,
    ) -> Transaction:
        """
        Create a new transaction.
        """
        if not isinstance(transaction_type, TransactionType):
            raise ValueError("Invalid transaction type.")

        # Validate accounts
        if transaction_type == TransactionType.TRANSFER:
            if not source_account_id or not destination_account_id:
                raise ValueError("Source and destination accounts are required for transfers.")
            source_account = self.account_service.get_account_by_id(db, source_account_id)
            destination_account = self.account_service.get_account_by_id(db, destination_account_id)
            if not source_account or not destination_account:
                raise AccountNotFoundError("One or both accounts not found.")
            if source_account.balance < amount:
                raise InsufficientFundsError("Insufficient funds in the source account.")
            source_account.balance -= amount
            destination_account.balance += amount
        elif transaction_type == TransactionType.DEPOSIT:
            if not destination_account_id:
                raise ValueError("Destination account is required for deposits.")
            destination_account = self.account_service.get_account_by_id(db, destination_account_id)
            if not destination_account:
                raise AccountNotFoundError("Destination account not found.")
            cash_holding_account = self.account_service.get_administrative_account(db, "Cash Holding Account")
            if not cash_holding_account:
                raise AccountNotFoundError("Cash Holding Account not found.")
            cash_holding_account.balance -= amount
            destination_account.balance += amount
            source_account_id = cash_holding_account.id
        elif transaction_type == TransactionType.WITHDRAW:
            if not source_account_id:
                raise ValueError("Source account is required for withdrawals.")
            source_account = self.account_service.get_account_by_id(db, source_account_id)
            if not source_account:
                raise AccountNotFoundError("Source account not found.")
            if source_account.balance < amount:
                raise InsufficientFundsError("Insufficient funds in the source account.")
            cash_disbursement_account = self.account_service.get_administrative_account(db, "Cash Disbursement Account")
            if not cash_disbursement_account:
                raise AccountNotFoundError("Cash Disbursement Account not found.")
            source_account.balance -= amount
            cash_disbursement_account.balance += amount
            destination_account_id = cash_disbursement_account.id

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
