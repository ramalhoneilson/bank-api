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
from api.config.config import CASH_HOLDING_ACCOUNT_ID, CASH_DISBURSEMENT_ACCOUNT_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('./transaction_management_steps.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def generate_account_number(prefix='U'):
    """Generate a unique account number."""
    return f"{prefix}-{str(uuid.uuid4())[:8]}"


def create_user_account(context, balance=0) -> BankAccount:
    """Helper function to create a user account"""
    account = BankAccount(
        account_number=generate_account_number(),
        account_type=AccountType.USER,
        status=AccountStatus.ACTIVE,
        balance=Decimal(str(balance))
    )
    context.db_session.add(account)
    context.db_session.flush()
    logger.info(f"User account created: {account.id}")
    return account


def create_admin_account(context, prefix='A', balance=0):
    """Helper function to create an administrative account"""
    account = BankAccount(
        account_number=generate_account_number(prefix),
        account_type=AccountType.ADMINISTRATIVE,
        status=AccountStatus.ACTIVE,
        balance=Decimal(str(balance)),
        administrative_entity_id=1
    )
    context.db_session.add(account)
    context.db_session.flush()
    logger.info(f"Admin account created: {account.id}")
    return account


@given('I have a user with an account balance of {balance:d}')
def step_setup_accounts(context, balance=0):
    """Create a user account with specified balance"""
    try:
        context.user1_account = create_user_account(context, balance)
        account = context.db_session.query(BankAccount).filter(
            BankAccount.id == context.user1_account.id
        ).first()
        assert account is not None, f"Failed to create user account with ID {context.user1_account.id}"
        logger.info(f"User account created and verified: {context.user1_account.id}")

        context.db_session.commit()
    except Exception as e:
        context.db_session.rollback()
        logger.error(f"Error creating user account: {e}")
        raise


@given('I have cash holding account with balance of {balance:d}')
def step_setup_cash_holding_account(context, balance):
    """Create cash holding account with specified balance"""
    try:
        context.cash_holding_account = create_admin_account(context, prefix='CASH', balance=balance)

        account = context.db_session.query(BankAccount).filter(
            BankAccount.id == context.cash_holding_account.id
        ).first()
        assert account is not None, f"Failed to create cash holding account with ID {context.cash_holding_account.id}"
        logger.info(f"Cash holding account created and verified: {context.cash_holding_account.id}")

        context.db_session.commit()
    except Exception as e:
        context.db_session.rollback()
        logger.error(f"Error creating cash holding account: {e}")
        raise


@given('I have cash disbursement account with balance of {balance:d}')
def step_setup_admin_account(context, balance):
    context.cash_disbursement_account = create_admin_account(context, prefix='DISB', balance=balance)
    context.db_session.commit()


@given('I have a source account with a balance of {source_balance:d} and a destination account with balance of {dest_balance:d}')
def step_setup_source_and_destination_accounts(context, source_balance, dest_balance):
    context.source_account = create_user_account(context, balance=source_balance)
    context.destination_account = create_user_account(context, balance=dest_balance)
    context.db_session.commit()


@given('I have a source account that does not exist and a destination account with balance of {dest_balance:d}')
def step_setup_source_and_destination_accounts(context, dest_balance):
    context.invalid_source_account = 9999999
    context.destination_account = create_user_account(context, balance=dest_balance)
    context.db_session.commit()


@given('I have a user account with some transactions')
def step_setup_transactions(context):
    bank_account_dao = BankAccountDAO()
    transaction_dao = TransactionDAO()
    account_service = BankAccountService(bank_account_dao)
    transaction_service = TransactionService(account_service, transaction_dao)

    context.user_account_with_tx = create_user_account(context)
    # cash holding account
    context.cash_holding_account = create_admin_account(context, prefix='CASH', balance=100)

    # cash disbursement account
    context.cash_disbursement_account = create_admin_account(context, prefix='DISB', balance=100)

    context.transactions = [
        transaction_service.create_deposit_transaction(context.db_session, amount=10, source_account_id=context.cash_holding_account.id,
                                                       destination_account_id=context.user_account_with_tx.id),
        transaction_service.create_withdrawal(context.db_session, amount=5, source_account_id=context.user_account_with_tx.id,
                                              destination_account_id=context.cash_disbursement_account.id),
    ]
    context.db_session.commit()


@when('I make a deposit with amount "{amount:d}"')
def step_send_deposit_request(context, amount):

    user_account = context.db_session.query(BankAccount).get(context.user1_account.id)
    logger.info(f"User account state: {user_account and user_account.balance}")

    cash_account = context.db_session.query(BankAccount).get(context.cash_holding_account.id)
    logger.info(f"Cash account state: {cash_account and cash_account.balance}")

    context.transaction_data = {
        "amount": amount,
        "source_account_id": context.cash_holding_account.id,
        "destination_account_id": context.user1_account.id
    }

    # Make the request
    context.response = context.client.post("/api/v1/transactions/deposit", json=context.transaction_data)

    logger.info(f"Response status: {context.response.status_code}")
    logger.info(f"Response body: {context.response.json()}")

    context.db_session.refresh(context.user1_account)
    context.db_session.refresh(context.cash_holding_account)


@when('I make a deposit with amount "{amount:d}" to an account that does not exist')
def step_send_deposit_request(context, amount):
    invalid_account_id = 999999
    cash_account = context.db_session.query(BankAccount).get(context.cash_holding_account.id)
    logger.info(f"Cash account state: {cash_account and cash_account.balance}")

    context.transaction_data = {
        "amount": amount,
        "source_account_id": context.cash_holding_account.id,
        "destination_account_id": invalid_account_id
    }

    # Make the request
    context.response = context.client.post("/api/v1/transactions/deposit", json=context.transaction_data)

    logger.info(f"Response status: {context.response.status_code}")
    logger.info(f"Response body: {context.response.json()}")

    context.db_session.refresh(context.cash_holding_account)


@when('I make a withdraw with amount "{amount:d}"')
def step_send_withdraw_request(context, amount):
    context.transaction_data = {"amount": amount,
                                "source_account_id": context.user1_account.id,
                                "destination_account_id": context.cash_disbursement_account.id
                                }
    context.response = context.client.post("/api/v1/transactions/withdraw", json=context.transaction_data)


@when('I make a withdraw with amount "{amount:d}" from an account that does not exist')
def step_send_withdraw_request(context, amount):
    invalid_account_id = 999999
    context.transaction_data = {"amount": amount,
                                "source_account_id": invalid_account_id,
                                "destination_account_id": context.cash_disbursement_account.id
                                }
    context.response = context.client.post("/api/v1/transactions/withdraw", json=context.transaction_data)


@when('I make a transfer with amount "{amount:d}" from the source account to the destination account')
def step_send_transfer_request(context, amount):
    context.transaction_data = {
        "amount": amount,
        "source_account_id": context.source_account.id,
        "destination_account_id": context.destination_account.id
    }
    context.response = context.client.post("/api/v1/transactions/transfer", json=context.transaction_data)


@when('I make a transfer with amount "{amount:d}" from the invalid source account to the destination account')
def step_send_transfer_request(context, amount):
    context.transaction_data = {
        "amount": amount,
        "source_account_id": context.invalid_source_account,
        "destination_account_id": context.destination_account.id
    }
    context.response = context.client.post("/api/v1/transactions/transfer", json=context.transaction_data)


@then('the response should contain the deposit transaction details')
def step_check_deposit_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.DEPOSIT.value, f"Transaction type should be DEPOSIT but got {response_data['transaction_type']}"
    assert response_data['amount'] == float(context.transaction_data['amount']), f"Amount mismatch. Expected {context.transaction_data['amount']} but got {response_data['amount']}"
    assert response_data['destination_account_id'] == context.transaction_data['destination_account_id'], "Destination account mismatch"
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the withdrawal transaction details')
def step_check_withdrawal_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.WITHDRAW.value, f"Transaction type should be WITHDRAW but got {response_data['transaction_type']}"
    assert response_data['amount'] == float(context.transaction_data['amount'])
    assert response_data['source_account_id'] == context.transaction_data['source_account_id']
    assert 'id' in response_data
    assert 'timestamp' in response_data


@then('the response should contain the transfer transaction details')
def step_check_transfer_response(context):
    response_data = context.response.json()
    assert response_data['transaction_type'] == TransactionType.TRANSFER.value, f"Transaction type should be TRANSFER but got {response_data['transaction_type']}"
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


@then('the cash holding account balance should be {balance:d}')
def step_check_admin_balance(context, balance):
    context.db_session.refresh(context.cash_holding_account)
    assert context.cash_holding_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.cash_holding_account.balance}"


@then('the user account balance should be {balance:d}')
def step_check_first_user_balance(context, balance):
    context.db_session.refresh(context.user1_account)
    assert context.user1_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.user1_account.balance}"


@then('the source account balance should be {balance:d}')
def step_check_first_user_balance(context, balance):
    context.db_session.refresh(context.source_account)
    assert context.source_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.source_account.balance}"


@then('the destination account balance should be {balance:d}')
def step_check_second_user_balance(context, balance):
    context.db_session.refresh(context.destination_account)
    assert context.destination_account.balance == Decimal(str(balance)), \
        f"Expected balance {balance}, got {context.destination_account.balance}"


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
