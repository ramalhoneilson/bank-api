import pytest
from decimal import Decimal
from api.models.bank_account import BankAccount
from api.models.customer import Customer
import uuid


@pytest.fixture
def system_customer(db_session):
    customer = Customer(customer_name="System")
    db_session.add(customer)
    db_session.flush()
    return customer


@pytest.fixture
def cash_holding_account(db_session, system_customer):
    account = BankAccount(
        account_number=str(uuid.uuid4()),
        balance=Decimal('10000'),
        customer_id=system_customer.id,
        account_type="USER",
        status="ACTIVE"
    )
    db_session.add(account)
    db_session.flush()
    return account


@pytest.fixture
def cash_disbursement_account(db_session, system_customer):
    account = BankAccount(
        account_number=str(uuid.uuid4()),
        balance=Decimal('10000'),
        customer_id=system_customer.id,
        account_type="USER",
        status="ACTIVE"
    )
    db_session.add(account)
    db_session.flush()
    return account


@pytest.fixture
def user_account(db_session, system_customer):
    account = BankAccount(
        account_number=str(uuid.uuid4()),
        balance=Decimal('1000'),
        customer_id=system_customer.id,
        account_type="USER",
        status="ACTIVE"
    )
    db_session.add(account)
    db_session.flush()
    return account
