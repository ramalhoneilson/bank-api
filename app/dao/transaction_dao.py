from sqlalchemy.orm import Session
from app.models.transaction import Transaction


class TransactionDAO:
    def create_transaction(self, db: Session, transaction: Transaction) -> Transaction:
        """
        Creates a new transaction record.
        """
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> Transaction:
        """
        Fetchs a transaction by its ID.
        """
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_transactions_by_account_id(self, db: Session, account_id: int) -> list[Transaction]:
        """
        Fetch all transactions for a given account (either as source or destination).
        """
        return (
            db.query(Transaction)
            .filter(
                (Transaction.source_account_id == account_id) |
                (Transaction.destination_account_id == account_id)
            )
            .all()
        )
