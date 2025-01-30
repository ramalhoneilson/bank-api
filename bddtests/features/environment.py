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

logger = logging.getLogger(__name__)


def before_all(context):
    """Initialize FastAPI test client"""
    context.client = TestClient(api)


def before_scenario(context, scenario):
    """Initialize database and test data before each scenario"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    context.db_session = TestingSessionLocal()

    setup_test_data(context.db_session)


def after_scenario(context, scenario):
    """Clean up after each scenario"""
    if hasattr(context, 'db_session'):
        context.db_session.close()


def setup_test_data(db_session):
    """Set up all necessary test data"""
    try:
        customer1 = Customer(
            id=1,
            customer_name="Test Customer 1"
        )
        db_session.add(customer1)

        customer2 = Customer(
            id=2,
            customer_name="test2@example.com"
        )
        db_session.add(customer2)

        admin_entity = AdministrativeEntity(
            id=1,
            corporate_name="Test Admin Entity"
        )
        db_session.add(admin_entity)

        cash_account = BankAccount(
            id=1,
            account_number="CASH-001",
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=Decimal('1000000'),
            administrative_entity_id=1
        )
        db_session.add(cash_account)

        disbursement_account = BankAccount(
            id=2,
            account_number="CASH-002",
            account_type=AccountType.ADMINISTRATIVE,
            status=AccountStatus.ACTIVE,
            balance=Decimal('0'),
            administrative_entity_id=1
        )
        db_session.add(disbursement_account)

        db_session.commit()

    except Exception as e:
        db_session.rollback()
        logger.debug(f"Test data already exists or other error: {e}")

    finally:
        db_session.expire_all()
