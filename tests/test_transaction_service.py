import uuid
import pytest
from decimal import Decimal
from api.models.bank_account import BankAccount
from api.models.transaction import Transaction, TransactionType
from api.services.transaction_service import TransactionService
from api.utils.exceptions import InsufficientFundsError, AccountNotFoundError
from api.dao.transaction_dao import TransactionDAO
from api.services.bank_account_service import BankAccountService
from tests.conftests import db_session, engine, tables
from tests.fixtures import cash_holding_account, system_customer, user_account, cash_disbursement_account
from api.dao.bank_account_dao import BankAccountDAO


@pytest.fixture
def bank_account_dao():
    return BankAccountDAO()

@pytest.fixture
def bank_account_service(bank_account_dao):
    return BankAccountService(bank_account_dao)


@pytest.fixture
def transaction_dao():
    return TransactionDAO()


@pytest.fixture
def transaction_service(bank_account_service, transaction_dao):
    return TransactionService(bank_account_service, transaction_dao)


class TestTransactionService:
    def test_successful_deposit(self, db_session, cash_holding_account, user_account, transaction_service):
        amount = Decimal('100')

        transaction = transaction_service.create_deposit_transaction(
            db_session,
            amount=amount,
            source_account_id=cash_holding_account.id,
            destination_account_id=user_account.id
        )

        db_session.refresh(cash_holding_account)
        db_session.refresh(user_account)

        assert transaction.amount == amount
        assert transaction.transaction_type == TransactionType.DEPOSIT
        assert transaction.source_account_id == cash_holding_account.id
        assert transaction.destination_account_id == user_account.id
        assert cash_holding_account.balance == Decimal('9900')
        assert user_account.balance == Decimal('1100')

    def test_insufficient_funds_transfer(self, db_session, user_account, cash_holding_account, transaction_service):

        amount = Decimal('2000')

        with pytest.raises(InsufficientFundsError):
            transaction_service.create_transfer(
                db_session,
                amount=amount,
                source_account_id=user_account.id,
                destination_account_id=cash_holding_account.id
            )

    def test_deposit_with_negative_amount(self, db_session, transaction_service):

        with pytest.raises(ValueError, match="Amount must be positive"):
            transaction_service.create_deposit_transaction(
                db_session,
                amount=Decimal('-100'),
                source_account_id=1,
                destination_account_id=3
            )

    def test_deposit_with_missing_destination(self, db_session, transaction_service):

        with pytest.raises(ValueError, match="Destination account is required"):
            transaction_service.create_deposit_transaction(
                db_session,
                amount=Decimal('100'),
                source_account_id=1,
                destination_account_id=None
            )

    def test_successful_transfer(self, db_session, user_account, transaction_service):

        other_account = BankAccount(
            account_number=str(uuid.uuid4()),
            balance=Decimal('500')
        )
        db_session.add(other_account)
        db_session.flush()
        amount = Decimal('100')

        transaction = transaction_service.create_transfer(
            db_session,
            amount=amount,
            source_account_id=user_account.id,
            destination_account_id=other_account.id
        )

        db_session.refresh(user_account)
        db_session.refresh(other_account)

        assert transaction.amount == amount
        assert transaction.transaction_type == TransactionType.TRANSFER
        assert transaction.source_account_id == user_account.id
        assert transaction.destination_account_id == other_account.id
        assert user_account.balance == Decimal('900')
        assert other_account.balance == Decimal('600')

    def test_transfer_insufficient_funds(self, db_session, user_account, transaction_service):

        other_account = BankAccount(
            account_number=str(uuid.uuid4()),
            balance=Decimal('500')
        )
        db_session.add(other_account)
        db_session.flush()

        with pytest.raises(InsufficientFundsError):
            transaction_service.create_transfer(
                db_session,
                amount=Decimal('2000'),
                source_account_id=user_account.id,
                destination_account_id=other_account.id
            )

    def test_successful_withdrawal(self, db_session, user_account, cash_disbursement_account, transaction_service):

        amount = Decimal('100')

        transaction = transaction_service.create_withdrawal(
            db_session,
            amount=amount,
            source_account_id=user_account.id,
            destination_account_id=cash_disbursement_account.id
        )

        
        db_session.refresh(user_account)
        db_session.refresh(cash_disbursement_account)

        assert transaction.amount == amount
        assert transaction.transaction_type == TransactionType.WITHDRAW
        assert transaction.source_account_id == user_account.id
