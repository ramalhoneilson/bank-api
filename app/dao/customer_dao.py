from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate


class CustomerDAO:
    def create_customer(self, db: Session, customer_data: CustomerCreate) -> Customer:
        db_customer = Customer(
            name=customer_data.name,
        )

        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)

        return db_customer

    def get_customer_by_id(self, db: Session, customer_id: int) -> Customer:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    def get_all_customers(self, db: Session) -> list[Customer]:
        return db.query(Customer).all()
