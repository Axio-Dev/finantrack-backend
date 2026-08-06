from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import transaction

from categories.selectors import get_category_by_movement_type
from transactions.models import Transaction


def create_transaction(
    *,
    name: str,
    description="",
    amount: Decimal,
    movement_type: str,
    payment_method: str,
    user,
    transaction_date: date,
    category_id: str,
    credit_card_id: str | None = None,
    subscription_id: str | None = None,
) -> Transaction:
    """
    Creates a Transaction for the given user.

    The selected category must match the transaction movement type.
    Model validations are executed before saving.

    Args:
        name: Transaction display name.
        description: Optional transaction description.
        amoutn: Positive transaction amount.
        movement_type: Either income or expense.
        payment_method: Payment method used for the transaction.
        user: User that owns the transaction.
        transaction_date: Date when the transaction were performed
        category_id: Selected category ID.
        credit_card_id: Optional credit card ID for credit payments.
        subscription_id: Optional subscription ID when transaction come from a subscription.

    Raises:
        PermissionDenied: If user is missing.
        ValidationError: If category or model validation fails.

    Returns:
        The created transaction.
    """

    if user is None or not user.is_authenticated:
        raise PermissionDenied("You need to be authenticated to perform this action.")

    category = get_category_by_movement_type(
        category_id=category_id, movement_type=movement_type
    )

    with transaction.atomic():
        transaction_obj = Transaction.objects.create(
            user=user,
            name=name,
            description=description,
            amount=amount,
            movement_type=movement_type,
            transaction_date=transaction_date,
            category_id=category.id,
            credit_card_id=credit_card_id,
            subscription_id=subscription_id,
            payment_method=payment_method,
        )

        # Calls the model validations
        transaction_obj.full_clean()

        # If the validation were successful, save the transaction in DB
        transaction_obj.save()

    return transaction_obj
