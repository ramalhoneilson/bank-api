import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database.base import Base
from api.models.bank_account import BankAccount
from api.models.customer import Customer
from api.models.transaction import Transaction
from api.models.administrative_entity import AdministrativeEntity



@pytest.fixture(scope="session")
def engine():
    # I decided to use an in-memory SQLite database for tests
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Returns a SQLAlchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
