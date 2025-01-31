# debug_transactions.py
import logging
import os
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.database.base import Base
from api.models.customer import Customer
from api.models.administrative_entity import AdministrativeEntity
from api.models.bank_account import BankAccount, AccountType, AccountStatus
from api.services.transaction_service import TransactionService
from api.services.bank_account_service import BankAccountService
from api.dao.transaction_dao import TransactionDAO
from api.dao.bank_account_dao import BankAccountDAO

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_FILE = "./test.db"


class TestContext:
    def __init__(self):
        self.cleanup_database()
        self.setup_database()
        self.setup_test_data()
        self.setup_services()

    def cleanup_database(self):
        """Remove existing database file"""
        try:
            if os.path.exists(DB_FILE):
                logger.info("Removing existing database file...")
                os.remove(DB_FILE)
        except Exception as e:
            logger.error(f"Error cleaning up database: {e}")
            raise e

    def setup_database(self):
        """Initialize fresh database"""
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=self.engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session = TestingSessionLocal()

    def setup_test_data(self):
        """Set up initial test data"""
        try:
            # Create test customers
            customer1 = Customer(
                id=1,
                customer_name="Test Customer 1"
            )
            self.db_session.add(customer1)

            customer2 = Customer(
                id=2,
                customer_name="test2@example.com"
            )
            self.db_session.add(customer2)

            # Create test administrative entity
            admin_entity = AdministrativeEntity(
                id=1,
                tax_id="123456789",
                corporate_name="Test Admin Entity"
            )
            self.db_session.add(admin_entity)

            # Create cash holding account
            cash_account = BankAccount(
                id=1,  # Cash holding account ID
                account_number="CASH-001",
                account_type=AccountType.ADMINISTRATIVE,
                status=AccountStatus.ACTIVE,
                balance=Decimal('1000000'),
                administrative_entity_id=1
            )
            self.db_session.add(cash_account)

            # Create cash disbursement account
            disbursement_account = BankAccount(
                id=2,  # Cash disbursement account ID
                account_number="CASH-002",
                account_type=AccountType.ADMINISTRATIVE,
                status=AccountStatus.ACTIVE,
                balance=Decimal('0'),
                administrative_entity_id=1
            )
            self.db_session.add(disbursement_account)

            # Create a test user account
            user_account = BankAccount(
                id=3,
                account_number="USER-001",
                account_type=AccountType.USER,
                status=AccountStatus.ACTIVE,
                balance=Decimal('100'),
                customer_id=1
            )
            self.db_session.add(user_account)

            self.db_session.commit()
            logger.info("Test data setup completed successfully")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error setting up test data: {e}")
            raise e

    def setup_services(self):
        """Initialize services"""
        self.bank_account_dao = BankAccountDAO()
        self.transaction_dao = TransactionDAO()
        self.bank_account_service = BankAccountService(self.bank_account_dao)
        self.transaction_service = TransactionService(
            self.bank_account_service,
            self.transaction_dao
        )

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
        if hasattr(self, 'engine'):
            self.engine.dispose()


def main():
    """Main debug function"""
    context = None
    try:
        context = TestContext()

        # Debug deposit
        logger.info("Testing deposit...")
        # print initial balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Initial user account balance: {user_account.balance}")

        deposit_transaction = context.transaction_service.create_deposit_transaction(
            context.db_session,
            amount=Decimal('50'),
            destination_account_id=3
        )
        logger.info(f"Deposit transaction created: {deposit_transaction.id}")
        # print final balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Final user account balance: {user_account.balance}")

        # Debug withdrawal
        logger.info("Testing withdrawal...")
        # print initial balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Initial user account balance: {user_account.balance}")
        withdrawal_transaction = context.transaction_service.create_withdrawal(
            context.db_session,
            amount=Decimal('30'),
            source_account_id=3
        )
        logger.info(f"Withdrawal transaction created: {withdrawal_transaction.id}")
        # print final balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Final user account balance: {user_account.balance}")

        # Debug transfer
        logger.info("Testing transfer...")
        # print initial balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Initial source account balance: {user_account.balance}")
        # print initial balance from all accounts involved
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 1)
        logger.info(f"Initial destination account balance: {user_account.balance}")

        transfer_transaction = context.transaction_service.create_transfer(
            context.db_session,
            amount=Decimal('20'),
            source_account_id=3,
            destination_account_id=1
        )
        logger.info(f"Transfer transaction created: {transfer_transaction.id}")

        # Check final balances
        user_account = context.bank_account_dao.get_account_by_id(
            context.db_session, 3)
        logger.info(f"Final user account balance: {user_account.balance}")

    except Exception as e:
        logger.error(f"Error during testing: {e}")
        raise e
    finally:
        if context:
            context.cleanup()


if __name__ == "__main__":
    main()
