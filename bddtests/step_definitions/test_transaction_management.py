import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from api.main import app
from api.models.bank_account import BankAccount, AccountType, AccountStatus
from api.models.customer import Customer
from api.models.administrative_entity import AdministrativeEntity
from api.dao.bank_account_dao import BankAccountDAO
from api.dao.transaction_dao import TransactionDAO
from api.services.bank_account_service import BankAccountService
from api.services.transaction_service import TransactionService
from sqlalchemy.orm import Session
import logging
import uuid
from tests.conftests import db_session, engine, tables
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

scenarios('../features/transaction_management.feature')


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    yield
    # Clean up all tables after each test
    for table in reversed(tables):
        db_session.execute(f'DELETE FROM {table.name}')
    db_session.commit()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def context():
    class Context:
        pass
    return Context()


def generate_account_number():
    """Generate a unique account number."""
    return f"ACC-{str(uuid.uuid4())[:8]}"


@pytest.fixture(autouse=True)
def setup_test_data(db_session: Session):
    """Setup test customers and administrative entities needed for bank accounts."""
    try:
        # Create test customer 1
        customer1 = Customer(
            id=1,
            customer_name="Test Customer 1"
        )
        db_session.add(customer1)

        # Create test customer 2
        customer2 = Customer(
            id=2,
            customer_name="test2@example.com"
        )
        db_session.add(customer2)

        # Create test administrative entity
        admin_entity = AdministrativeEntity(
            id=1,
            corporate_name="Test Admin Entity"
        )
        db_session.add(admin_entity)

        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.debug(f"Test data already exists: {e}")


# Alternative 1: Using parse instead of re
@given(parsers.parse('I have a user account with ID {account_id:d} and an administrative account with ID {admin_account_id:d}'))
def step_setup_accounts(db_session: Session, context, account_id: int, admin_account_id: int):
    bank_account_dao = BankAccountDAO()

    # Try to get or create user account
    context.user_account = bank_account_dao.get_account_by_id(db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=0,
            customer_id=1
        )
        db_session.add(context.user_account)

    # Try to get or create admin account
    context.admin_account = bank_account_dao.get_account_by_id(db_session, admin_account_id)
    if not context.admin_account:
        context.admin_account = BankAccount(
            id=admin_account_id,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=0,
            administrative_entity_id=1
        )
        db_session.add(context.admin_account)

    db_session.commit()
    db_session.refresh(context.user_account)
    db_session.refresh(context.admin_account)


@given(parsers.parse('I have an administrative account with ID {admin_account_id:d}'))
def step_setup_admin_account(db_session: Session, context, admin_account_id: int):
    bank_account_dao = BankAccountDAO()
    context.admin_account = bank_account_dao.get_account_by_id(db_session, admin_account_id)
    if not context.admin_account:
        context.admin_account = BankAccount(
            id=admin_account_id,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=0,
            administrative_entity_id=1
        )
        db_session.add(context.admin_account)
        db_session.commit()
        db_session.refresh(context.admin_account)


@given(parsers.parse('the user account has a balance of {balance:d}'))
def step_set_user_balance(db_session: Session, context, balance: int):
    context.user_account.balance = balance
    db_session.commit()
    db_session.refresh(context.user_account)


@given(parsers.parse('the administrative account has a balance of {balance:d}'))
def step_set_admin_balance(db_session: Session, context, balance: int):
    context.admin_account.balance = balance
    db_session.commit()
    db_session.refresh(context.admin_account)


@given(parsers.parse('I have a user account with ID {account_id:d} and a balance of {balance:d}'))
def step_setup_user_account_with_balance(db_session: Session, context, account_id: int, balance: int):
    bank_account_dao = BankAccountDAO()
    context.user_account = bank_account_dao.get_account_by_id(db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=balance,
            customer_id=1
        )
        db_session.add(context.user_account)
        db_session.commit()
        db_session.refresh(context.user_account)
    else:
        context.user_account.balance = balance
        db_session.commit()
        db_session.refresh(context.user_account)


@given(parsers.parse('I have another user account with ID {account_id:d} and a balance of {balance:d}'))
def step_setup_second_account(db_session: Session, context, account_id: int, balance: int):
    bank_account_dao = BankAccountDAO()
    context.second_user_account = bank_account_dao.get_account_by_id(db_session, account_id)
    if not context.second_user_account:
        context.second_user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=balance,
            customer_id=2
        )
        db_session.add(context.second_user_account)
        db_session.commit()
        db_session.refresh(context.second_user_account)
    else:
        context.second_user_account.balance = balance
        db_session.commit()
        db_session.refresh(context.second_user_account)


@given(parsers.parse('I have a user account with ID {account_id:d} and some transactions'))
def step_setup_transactions(db_session: Session, context, account_id: int):
    bank_account_dao = BankAccountDAO()
    context.user_account = bank_account_dao.get_account_by_id(db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=0,
            customer_id=1
        )
        db_session.add(context.user_account)
        db_session.commit()
        db_session.refresh(context.user_account)

    transaction_dao = TransactionDAO()
    account_service = BankAccountService(bank_account_dao)
    transaction_service = TransactionService(account_service, transaction_dao)

    # Create test transactions
    admin_account = bank_account_dao.get_account_by_id(db_session, 999)
    if not admin_account:
        admin_account = BankAccount(
            id=999,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=1000,
            administrative_entity_id=1
        )
        db_session.add(admin_account)
        db_session.commit()

    context.transactions = [
        transaction_service.create_deposit_transaction(db_session, amount=10, destination_account_id=account_id),
        transaction_service.create_withdrawal(db_session, amount=5, source_account_id=account_id)
    ]


@when(parsers.parse('I send a POST request to "/api/v1/transactions/deposit" with amount {amount:d} and account_id {account_id:d}'))
def step_send_deposit_request(client, context, amount: int, account_id: int):
    context.transaction_data = {
        "amount": amount,
        "account_id": account_id,
        "source_account_id": context.admin_account.id  # Use the admin account as source
    }
    context.response = client.post("/api/v1/transactions/deposit", json=context.transaction_data)
    log_response(context.response)


@when(parsers.parse('I send a POST request to "/api/v1/transactions/withdraw" with amount {amount:d} and account_id {account_id:d}'))
def step_send_withdraw_request(client, context, amount: int, account_id: int):
    context.transaction_data = {"amount": amount, "account_id": account_id}
    context.response = client.post("/api/v1/transactions/withdraw", json=context.transaction_data)
    log_response(context.response)


@when(parsers.parse('I send a POST request to "/api/v1/transactions/transfer" with amount {amount:d}, source_account_id {source_account_id:d}, and destination_account_id {dest_account_id:d}'))
def step_send_transfer_request(client, context, amount: int, source_account_id: int, dest_account_id: int):
    context.transaction_data = {
        "amount": amount,
        "source_account_id": source_account_id,
        "destination_account_id": dest_account_id
    }
    context.response = client.post("/api/v1/transactions/transfer", json=context.transaction_data)
    log_response(context.response)


@when(parsers.parse('I send a GET request to "/api/v1/transactions/{account_id:d}"'))
def step_send_get_request(client, context, account_id: int):
    context.response = client.get(f"/api/v1/transactions/{account_id}")
    log_response(context.response)


def log_response(response):
    logger.debug(f"Response status: {response.status_code}")
    try:
        response_body = response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")


@then(parsers.parse('the response status code should be {status_code:d}'))
def step_check_status_code(context, status_code: int):
    assert context.response.status_code == status_code, f"Expected {status_code}, got {context.response.status_code}. Response: {context.response.text}"


@then('the response should contain the deposit transaction details')
def step_check_deposit_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == 'DEPOSIT'
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['destination_account_id'] == context.transaction_data['account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the withdrawal transaction details')
def step_check_withdrawal_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == 'WITHDRAWAL'
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['source_account_id'] == context.transaction_data['account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the transfer transaction details')
def step_check_transfer_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == 'TRANSFER'
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['source_account_id'] == context.transaction_data['source_account_id']
    assert response_data['destination_account_id'] == context.transaction_data['destination_account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then(parsers.parse('the response should contain an "{error_type}" error message'))
def step_check_error_message(context, error_type: str):
    response_data = context.response.json()
    assert 'detail' in response_data
    expected_variations = {
        'Account not found': ['account not found', 'one or both accounts not found'],
        'Insufficient funds': ['insufficient funds']
    }
    error_message = response_data['detail'].lower()
    expected_messages = expected_variations.get(error_type, [error_type.lower()])
    assert any(msg in error_message for msg in expected_messages), \
        f"Expected one of {expected_messages} in '{error_message}'"


@then(parsers.parse('the user account balance should be {balance:d}'))
def step_check_user_balance(db_session: Session, context, balance: int):
    db_session.refresh(context.user_account)
    assert context.user_account.balance == balance, f"Expected balance {balance}, got {context.user_account.balance}"


@then(parsers.parse('the administrative account balance should be {balance:d}'))
def step_check_admin_balance(db_session: Session, context, balance: int):
    db_session.refresh(context.admin_account)
    assert context.admin_account.balance == balance, f"Expected balance {balance}, got {context.admin_account.balance}"


@then(parsers.parse('the first user account balance should be {balance:d}'))
def step_check_first_user_balance(db_session: Session, context, balance: int):
    db_session.refresh(context.user_account)
    assert context.user_account.balance == balance, f"Expected balance {balance}, got {context.user_account.balance}"


@then(parsers.parse('the second user account balance should be {balance:d}'))
def step_check_second_user_balance(db_session: Session, context, balance: int):
    db_session.refresh(context.second_user_account)
    assert context.second_user_account.balance == balance, f"Expected balance {balance}, got {context.second_user_account.balance}"



@then(parsers.parse('the response should contain a list of transactions for account {account_id:d}'))
def step_check_transaction_list(context, account_id: int):
    response_data = context.response.json()
    assert isinstance(response_data, list), "Response should be a list"
    assert len(response_data) > 0, "Transaction list should not be empty"
    for transaction in response_data:
        assert isinstance(transaction, dict)
        assert 'id' in transaction
        assert 'amount' in transaction
        assert 'transaction_type' in transaction
        assert 'timestamp' in transaction
        assert (transaction['source_account_id'] == account_id or
                transaction['destination_account_id'] == account_id)
