from sqlalchemy.orm import Session
from api.models.customer import Customer


class CustomerDAO:
    def create_customer(self, db: Session, customer_data: dict) -> Customer:
        customer_dict = customer_data.model_dump()
        customer = Customer(**customer_dict)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def get_customer_by_id(self, db: Session, customer_id: int) -> Customer:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    def get_all_customers(self, db: Session) -> list[Customer]:
        return db.query(Customer).all()
