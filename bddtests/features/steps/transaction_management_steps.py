from behave import given, when, then
from fastapi.testclient import TestClient
from api.models.bank_account import BankAccount, AccountType, AccountStatus
from api.models.customer import Customer
from api.models.administrative_entity import AdministrativeEntity
from api.dao.bank_account_dao import BankAccountDAO
from api.dao.transaction_dao import TransactionDAO
from api.models.transaction import TransactionType
from api.services.bank_account_service import BankAccountService
from api.services.transaction_service import TransactionService
import logging
import uuid
from sqlalchemy.orm import Session
from decimal import Decimal

logger = logging.getLogger(__name__)


def generate_account_number():
    """Generate a unique account number."""
    return f"ACC-{str(uuid.uuid4())[:8]}"


@given('I have a user account with ID {account_id:d} and an administrative account with ID {admin_account_id:d}')
def step_setup_accounts(context, account_id, admin_account_id):
    bank_account_dao = BankAccountDAO()

    # Create user account if it doesn't exist
    context.user_account = bank_account_dao.get_account_by_id(context.db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=Decimal('0'),
            customer_id=1
        )
        context.db_session.add(context.user_account)

    # Create admin account if it doesn't exist
    context.admin_account = bank_account_dao.get_account_by_id(context.db_session, admin_account_id)
    if not context.admin_account:
        context.admin_account = BankAccount(
            id=admin_account_id,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=Decimal('0'),
            administrative_entity_id=1
        )
        context.db_session.add(context.admin_account)

    context.db_session.commit()
    context.db_session.refresh(context.user_account)
    context.db_session.refresh(context.admin_account)


@given('I have an administrative account with ID {admin_account_id:d}')
def step_setup_admin_account(context, admin_account_id):
    bank_account_dao = BankAccountDAO()
    context.admin_account = bank_account_dao.get_account_by_id(context.db_session, admin_account_id)
    if not context.admin_account:
        context.admin_account = BankAccount(
            id=admin_account_id,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=0,
            administrative_entity_id=1
        )
        context.db_session.add(context.admin_account)
        context.db_session.commit()
        context.db_session.refresh(context.admin_account)


@given('the user account has a balance of {balance:d}')
def step_set_user_balance(context, balance):
    context.user_account.balance = Decimal(str(balance))
    context.db_session.commit()
    context.db_session.refresh(context.user_account)


@given('the administrative account has a balance of {balance:d}')
def step_set_admin_balance(context, balance):
    context.admin_account.balance = Decimal(str(balance))
    context.db_session.commit()
    context.db_session.refresh(context.admin_account)


@given('I have a user account with ID {account_id:d} and a balance of {balance:d}')
def step_setup_user_account_with_balance(context, account_id, balance):
    bank_account_dao = BankAccountDAO()
    context.user_account = bank_account_dao.get_account_by_id(context.db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=balance,
            customer_id=1
        )
        context.db_session.add(context.user_account)
        context.db_session.commit()
        context.db_session.refresh(context.user_account)
    else:
        context.user_account.balance = balance
        context.db_session.commit()
        context.db_session.refresh(context.user_account)


@given('I have another user account with ID {account_id:d} and a balance of {balance:d}')
def step_setup_second_account(context, account_id, balance):
    bank_account_dao = BankAccountDAO()
    context.second_user_account = bank_account_dao.get_account_by_id(context.db_session, account_id)
    if not context.second_user_account:
        context.second_user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=balance,
            customer_id=2
        )
        context.db_session.add(context.second_user_account)
        context.db_session.commit()
        context.db_session.refresh(context.second_user_account)
    else:
        context.second_user_account.balance = balance
        context.db_session.commit()
        context.db_session.refresh(context.second_user_account)


@given('I have a user account with ID {account_id:d} and some transactions')
def step_setup_transactions(context, account_id):
    bank_account_dao = BankAccountDAO()
    transaction_dao = TransactionDAO()
    account_service = BankAccountService(bank_account_dao)
    transaction_service = TransactionService(account_service, transaction_dao)

    context.user_account = bank_account_dao.get_account_by_id(context.db_session, account_id)
    if not context.user_account:
        context.user_account = BankAccount(
            id=account_id,
            account_number=generate_account_number(),
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            balance=0,
            customer_id=1
        )
        context.db_session.add(context.user_account)
        context.db_session.commit()
        context.db_session.refresh(context.user_account)

    # Create test transactions
    admin_account = bank_account_dao.get_account_by_id(context.db_session, 999)
    if not admin_account:
        admin_account = BankAccount(
            id=999,
            account_number=generate_account_number(),
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=1000,
            administrative_entity_id=1
        )
        context.db_session.add(admin_account)
        context.db_session.commit()

    context.transactions = [
        transaction_service.create_deposit_transaction(context.db_session, amount=10, destination_account_id=account_id),
        transaction_service.create_withdrawal(context.db_session, amount=5, source_account_id=account_id)
    ]


@when('I send a POST request to "/api/v1/transactions/deposit" with amount {amount:d} and account_id {account_id:d}')
def step_send_deposit_request(context, amount, account_id):
    context.transaction_data = {
        "amount": amount,
        "account_id": account_id,
        "source_account_id": context.admin_account.id
    }
    context.response = context.client.post("/api/v1/transactions/deposit", json=context.transaction_data)


@when('I send a POST request to "/api/v1/transactions/withdraw" with amount {amount:d} and account_id {account_id:d}')
def step_send_withdraw_request(context, amount, account_id):
    context.transaction_data = {"amount": amount, "account_id": account_id}
    context.response = context.client.post("/api/v1/transactions/withdraw", json=context.transaction_data)


@when('I send a POST request to "/api/v1/transactions/transfer" with amount {amount:d}, source_account_id {source_account_id:d}, and destination_account_id {dest_account_id:d}')
def step_send_transfer_request(context, amount, source_account_id, dest_account_id):
    context.transaction_data = {
        "amount": amount,
        "source_account_id": source_account_id,
        "destination_account_id": dest_account_id
    }
    context.response = context.client.post("/api/v1/transactions/transfer", json=context.transaction_data)


@then('the response should contain the deposit transaction details')
def step_check_deposit_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.DEPOSIT
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['destination_account_id'] == context.transaction_data['account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the withdrawal transaction details')
def step_check_withdrawal_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.WITHDRAW
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['source_account_id'] == context.transaction_data['account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the transfer transaction details')
def step_check_transfer_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.TRANSFER
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['source_account_id'] == context.transaction_data['source_account_id']
    assert response_data['destination_account_id'] == context.transaction_data['destination_account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain an "{error_type}" error message')
def step_check_specific_error_message(context, error_type):
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


@then('the user account balance should be {balance:d}')
def step_check_user_balance(context, balance):
    context.db_session.refresh(context.user_account)
    assert context.user_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.user_account.balance}"


@then('the administrative account balance should be {balance:d}')
def step_check_admin_balance(context, balance):
    context.db_session.refresh(context.admin_account)
    assert context.admin_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.admin_account.balance}"


@then('the first user account balance should be {balance:d}')
def step_check_first_user_balance(context, balance):
    context.db_session.refresh(context.user_account)
    assert context.user_account.balance == balance, \
        f"Expected balance {balance}, got {context.user_account.balance}"


@then('the second user account balance should be {balance:d}')
def step_check_second_user_balance(context, balance):
    context.db_session.refresh(context.second_user_account)
    assert context.second_user_account.balance == balance, \
        f"Expected balance {balance}, got {context.second_user_account.balance}"


@then('the response should contain a list of transactions for account {account_id:d}')
def step_check_transaction_list(context, account_id):
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
