from django.db.models import QuerySet

from common.exceptions import ResourceNotFound
from transactions.models import Transaction


def get_transaction(*, transaction_id: str, user) -> Transaction:

    transaction = Transaction.objects.filter(
        id=transaction_id, user=user, is_active=True
    ).first()

    if transaction is None:
        raise ResourceNotFound("Transaction not found.")

    return transaction


def list_transactions(*, user) -> QuerySet[Transaction]:
    return Transaction.objects.filter(user=user, is_active=True)
