from sqlalchemy.orm import Session
from app.dao.customer_dao import CustomerDAO
from app.schemas.customer_schema import CustomerCreate, CustomerResponse


class CustomerService:
    def __init__(self, customer_dao: CustomerDAO):
        self.customer_dao = customer_dao

    def create_new_customer(self, db: Session, customer_data: CustomerCreate) -> CustomerResponse:
        if not customer_data.customer_name:
            raise ValueError("Customer name cannot be empty")

        created_customer = self.customer_dao.create_customer(db, customer_data)
        return CustomerResponse.model_validate(created_customer)

    def get_customer_by_id(self, db: Session, customer_id: int) -> CustomerResponse:
        customer = self.customer_dao.get_customer_by_id(db, customer_id)
        if customer:
            return CustomerResponse.model_validate(customer)
        return None

    def get_all_customers(self, db: Session) -> list[CustomerResponse]:
        customers = self.customer_dao.get_all_customers(db)
        return [CustomerResponse.model_validate(customer) for customer in customers]
