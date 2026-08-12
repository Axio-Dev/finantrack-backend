from django.core.exceptions import ValidationError

from transactions.models import Transaction


def get_transaction(*, transaction_id: str, user) -> Transaction:

    transaction = Transaction.objects.filter(
        id=transaction_id, user=user, is_active=True
    ).first()

    if transaction is None:
        raise ValidationError(
            {"transaction": "Selected transaction does not exist or is inactive."}
        )

    return transaction
