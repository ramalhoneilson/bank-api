import pytest
from api.dao.bank_account_dao import BankAccountDAO
from api.services.bank_account_service import BankAccountService
from api.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse
from api.models.bank_account import AccountType
from tests.fixtures import system_customer
from sqlalchemy.orm import attributes
from tests.fixtures import system_customer
from tests.conftests import db_session, engine, tables
from api.models.bank_account import AccountStatus


@pytest.fixture
def bank_account_dao():
    return BankAccountDAO()


@pytest.fixture
def bank_account_service(bank_account_dao):
    return BankAccountService(bank_account_dao)


class TestBankAccountService:

    def test_create_new_account(self, db_session, bank_account_service, system_customer):
        account_data = BankAccountCreate(
            balance=1000.0,
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            owner_id=system_customer.id
        )
        created_account = bank_account_service.create_new_account(db_session, account_data)

        assert isinstance(created_account, BankAccountResponse)
        assert created_account.balance == account_data.balance
        assert created_account.account_type == account_data.account_type
        assert created_account.status == account_data.status
        assert created_account.id is not None
        assert created_account.account_number is not None

    def test_get_administrative_account_found(self, db_session, bank_account_service, system_customer):
        admin_account = BankAccountDAO().create_account(db_session, BankAccountCreate(
            balance=0,
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            owner_id=system_customer.id
        ))

        retrieved_account = bank_account_service.get_administrative_account(db_session, admin_account.account_number)

        assert retrieved_account is not None
        assert isinstance(retrieved_account, BankAccountResponse)  # Check if the returned type is correct
        assert retrieved_account.account_type == AccountType.ADMINISTRATIVE

    def test_get_administrative_account_not_found(self, db_session, bank_account_service):
        retrieved_account = bank_account_service.get_administrative_account(db_session, "nonexistent_account")
        assert retrieved_account is None

    def test_get_all_accounts(self, db_session, bank_account_service, system_customer):  # Use system_customer
        # Create some more accounts for testing
        BankAccountDAO().create_account(db_session, BankAccountCreate(balance=0, account_type=AccountType.USER, status=AccountStatus.ACTIVE, owner_id=system_customer.id))
        BankAccountDAO().create_account(db_session, BankAccountCreate(balance=0, account_type=AccountType.USER, status=AccountStatus.ACTIVE, owner_id=system_customer.id))
        accounts = bank_account_service.get_all_accounts(db_session)

        assert isinstance(accounts, list)
        assert all(isinstance(account, BankAccountResponse) for account in accounts)
        assert len(accounts) >= 1

        for account in accounts:
            assert account.id is not None
            assert account.account_number is not None
            assert isinstance(account.balance, float)
            assert isinstance(account.account_type, AccountType)
            assert isinstance(account.status, AccountStatus)

    def test_get_account_by_id_found(self, db_session, bank_account_service, system_customer):
        account = BankAccountDAO().create_account(db_session, BankAccountCreate(balance=0, account_type=AccountType.USER, status=AccountStatus.ACTIVE, owner_id=system_customer.id))

        retrieved_account = bank_account_service.get_account_by_id(db_session, account.id)

        assert isinstance(retrieved_account, BankAccountResponse)
        assert retrieved_account.id == account.id
        assert retrieved_account.account_number is not None
        assert isinstance(retrieved_account.balance, float)
        assert isinstance(retrieved_account.account_type, AccountType)
        assert isinstance(retrieved_account.status, AccountStatus)

    def test_get_account_by_id_not_found(self, db_session, bank_account_service):
        retrieved_account = bank_account_service.get_account_by_id(db_session, 999)  # Nonexistent ID
        assert retrieved_account is None
