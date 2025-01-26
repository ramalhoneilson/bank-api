from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.transaction_service import TransactionService
from app.services.bank_account_service import BankAccountService
from app.dao.transaction_dao import TransactionDAO
from app.dao.bank_account_dao import BankAccountDAO
from app.schemas.transaction_schema import (
    DepositCreate,
    TransactionResponse,
)
from app.models.transaction import TransactionType
from app.utils.exceptions import AccountNotFoundError

from app.schemas.transaction_schema import (
    DepositCreate,
    WithdrawCreate,
    TransferCreate,
    TransactionResponse,
)
from app.models.transaction import TransactionType
from app.utils.exceptions import AccountNotFoundError, InsufficientFundsError
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transactions/deposit", response_model=TransactionResponse)
def deposit_funds(deposit_data: DepositCreate, db: Session = Depends(get_db)):
    """
    Deposit funds into an account. Deposits always move money from an administrative account to a user account.
    """
    try:
        logger.info(f"Processing deposit: {deposit_data}")
        transaction_dao = TransactionDAO()
        account_service = BankAccountService(BankAccountDAO())
        transaction_service = TransactionService(account_service, transaction_dao)

        transaction = transaction_service.create_deposit_transaction(
            db,
            amount=deposit_data.amount,
            destination_account_id=deposit_data.account_id,
        )

        return TransactionResponse(
            id=transaction.id,
            amount=float(transaction.amount),
            transaction_type=transaction.transaction_type.value,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            timestamp=transaction.timestamp,
        )

    except ValueError as e:
        logger.error(f"Validation error during deposit: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        logger.error(f"Account not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during deposit: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/transactions/withdraw", response_model=TransactionResponse)
def withdraw_funds(withdraw_data: WithdrawCreate, db: Session = Depends(get_db)):
    """
    Withdraw funds from an account.
    """
    try:
        logger.info(f"Processing withdrawal: {withdraw_data}")
        transaction_dao = TransactionDAO()
        account_service = BankAccountService(BankAccountDAO())
        transaction_service = TransactionService(account_service, transaction_dao)

        transaction = transaction_service.create_transaction(
            db,
            amount=withdraw_data.amount,
            source_account_id=withdraw_data.account_id,
        )

        return TransactionResponse(
            id=transaction.id,
            amount=float(transaction.amount),
            transaction_type=transaction.transaction_type.value,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            timestamp=transaction.timestamp,
        )

    except ValueError as e:
        logger.error(f"Validation error during withdrawal: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        logger.error(f"Account not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        logger.error(f"Insufficient funds: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during withdrawal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/transactions/transfer", response_model=TransactionResponse)
def transfer_funds(transfer_data: TransferCreate, db: Session = Depends(get_db)):
    """
    Transfer funds between two accounts.
    """
    try:
        logger.info(f"Processing transfer: {transfer_data}")
        transaction_dao = TransactionDAO()
        account_service = BankAccountService(BankAccountDAO())
        transaction_service = TransactionService(account_service, transaction_dao)

        transaction = transaction_service.create_transfer(
            db,
            amount=transfer_data.amount,
            source_account_id=transfer_data.source_account_id,
            destination_account_id=transfer_data.destination_account_id,
        )

        return TransactionResponse(
            id=transaction.id,
            amount=float(transaction.amount),
            transaction_type=transaction.transaction_type.value,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            timestamp=transaction.timestamp,
        )

    except ValueError as e:
        logger.error(f"Validation error during transfer: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        logger.error(f"Account not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        logger.error(f"Insufficient funds: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during transfer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
