from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.customer_account_service import CustomerAccountService
from app.dao.bank_account_dao import BankAccountDAO
from app.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse
from typing import List

router = APIRouter()


@router.post("/bank-accounts", response_model=BankAccountResponse)
def create_account(account_data: BankAccountCreate, db: Session = Depends(get_db)):
    """
    Create a new bank account for a given customer
    - customer
    - deposit amount
    - account type
    """
    try:
        account_dao = BankAccountDAO()
        account_service = CustomerAccountService(account_dao)

        new_account = account_service.create_new_account(db, account_data)
        return new_account

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bank-accounts", response_model=List[BankAccountResponse])
def list_all_accounts(db: Session = Depends(get_db)):
    """
    List all accounts in the system.
    """
    try:
        account_dao = BankAccountDAO()
        account_service = CustomerAccountService(account_dao)

        accounts = account_service.get_all_accounts(db)
        return accounts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
def get_account_details(account_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific account by its ID.
    """
    try:
        account_dao = BankAccountDAO()
        account_service = CustomerAccountService(account_dao)

        account = account_service.get_account_by_id(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
