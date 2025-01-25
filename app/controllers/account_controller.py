from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.account_service import AccountService
from app.dao.account_dao import AccountDAO
from app.schemas.account_schema import AccountCreate, AccountResponse

router = APIRouter()


@router.post("/accounts", response_model=AccountResponse)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new bank account for a given customer
    - customer
    - deposit amount
    - account type
    """
    try:
        account_dao = AccountDAO()
        account_service = AccountService(account_dao)

        new_account = account_service.create_new_account(db, account_data)
        return new_account

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
