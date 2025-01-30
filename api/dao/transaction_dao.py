from sqlalchemy.orm import Session
from sqlalchemy import select
from api.models.transaction import Transaction


class TransactionDAO:
    def create_transaction(self, db: Session, transaction: Transaction) -> Transaction:
        db.add(transaction)
        return transaction

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> Transaction:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_transactions_by_account_id(self, db: Session, account_id: int) -> list[Transaction]:
        stmt = select(Transaction).where(
            (Transaction.source_account_id == account_id) |
            (Transaction.destination_account_id == account_id)
        )
        return list(db.execute(stmt).scalars().all())
