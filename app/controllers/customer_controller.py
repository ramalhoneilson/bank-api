from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.customer_service import CustomerService
from app.dao.customer_dao import CustomerDAO
from app.schemas.customer_schema import CustomerCreate, CustomerResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/customers", response_model=CustomerResponse)
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer
    - customer_name
    """
    try:
        customer_dao = CustomerDAO()
        customer_service = CustomerService(customer_dao)
        logging.info(f"Creating new customer: {customer_data}")

        new_customer = customer_service.create_new_customer(db, customer_data)
        return new_customer

    except Exception as e:
        print(e)
        logging.error(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific customer by ID
    """
    try:
        logger.info(f"Fetching customer with ID: {customer_id}")
        customer_dao = CustomerDAO()
        customer_service = CustomerService(customer_dao)

        customer = customer_service.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers", response_model=list[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    """
    Get a list of all customers
    """
    try:
        customer_dao = CustomerDAO()
        customer_service = CustomerService(customer_dao)

        customers = customer_service.get_all_customers(db)
        return customers

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
