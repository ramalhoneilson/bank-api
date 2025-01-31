import logging
import os

os.environ["ENVIRONMENT"] = "local"

from api.main import api
from api.database.session import get_db
from api.database.base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient


logger = logging.getLogger(__name__)
# create a file based database to run tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def before_all(context):
    """Initialize test environment before all tests."""
    # Create all tables in the test database
    Base.metadata.drop_all(bind=engine)  # Ensure clean state
    Base.metadata.create_all(bind=engine)

    # Override the database dependency
    api.dependency_overrides[get_db] = override_get_db

    # Create test client
    context.client = TestClient(api)
    logger.info("Test environment initialized with in-memory database")


def before_scenario(context, scenario):
    """Set up fresh database session for each scenario."""
    context.db_session = TestingSessionLocal()

    # Set up initial test data
    setup_test_data(context.db_session)
    context.db_session.commit()
    logger.info(f"Database prepared for scenario: {scenario.name}")


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    if hasattr(context, 'db_session'):
        context.db_session.close()
    logger.info(f"Cleanup completed for scenario: {scenario.name}")


def setup_test_data(db_session):
    """Set up initial test data needed for all scenarios."""
    from api.models.administrative_entity import AdministrativeEntity

    try:
        # Create administrative entity
        admin_entity = AdministrativeEntity(
            corporate_name="Test Admin Entity",
            tax_id="1234567890"
        )
        db_session.add(admin_entity)
        db_session.flush()
        logger.info("Initial test data setup completed")
        return admin_entity
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error in test data setup: {e}")
        raise
