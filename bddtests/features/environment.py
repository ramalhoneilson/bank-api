from fastapi.testclient import TestClient
from api.main import api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database.base import Base
from api.models.customer import Customer
from api.models.administrative_entity import AdministrativeEntity
from api.models.bank_account import BankAccount, AccountType, AccountStatus
from decimal import Decimal
import logging
import os

logger = logging.getLogger(__name__)

# Define the database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def before_all(context):
    """Initialize FastAPI test client and ensure the database is clean."""
    # Delete the SQLite database file if it exists
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
            logger.debug("Existing test database deleted.")
        except Exception as e:
            logger.error(f"Error deleting test database: {e}")

    # Initialize the test client
    context.client = TestClient(api)

    # Create a new database
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    logger.debug("New test database created.")


def before_scenario(context, scenario):
    """Initialize database and test data before each scenario."""
    # Create a new database engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    context.db_session = TestingSessionLocal()

    # Set up test data
    setup_test_data(context.db_session)
    logger.debug("Test data set up for scenario.")


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    if hasattr(context, 'db_session'):
        context.db_session.close()
        logger.debug("Database session closed.")

    # Delete the SQLite database file to ensure a clean state for the next scenario
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
            logger.debug("Test database deleted after scenario.")
        except Exception as e:
            logger.error(f"Error deleting test database after scenario: {e}")


def setup_test_data(db_session):
    """Set up all necessary test data."""
    try:
        # Create test customers
        customer1 = Customer(
            customer_name="Test Customer 1"
        )
        db_session.add(customer1)

        customer2 = Customer(
            customer_name="test2@example.com"
        )
        db_session.add(customer2)

        # Create administrative entity
        admin_entity = AdministrativeEntity(
            corporate_name="Test Admin Entity"
        )
        db_session.add(admin_entity)

        # Create cash holding account
        cash_account = BankAccount(
            account_number="CASH-001",
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=Decimal('1000000'),
            administrative_entity_id=1
        )
        db_session.add(cash_account)

        # Create cash disbursement account
        disbursement_account = BankAccount(
            account_number="CASH-002",
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=Decimal('0'),
            administrative_entity_id=1
        )
        db_session.add(disbursement_account)

        db_session.commit()
        logger.debug("Test data created successfully.")

    except Exception as e:
        db_session.rollback()
        logger.error(f"Error setting up test data: {e}")

    finally:
        db_session.expire_all()
