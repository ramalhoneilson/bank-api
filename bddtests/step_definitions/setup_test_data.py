from api.models.customer import Customer
from api.models.administrative_entity import AdministrativeEntity
from sqlalchemy.orm import Session
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup_test_data(db_session: Session):
    """Setup test customers and administrative entities needed for bank accounts."""
    try:
        db_session.begin_nested()  # Create a savepoint

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

        yield
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error setting up test data: {e}")
        raise
