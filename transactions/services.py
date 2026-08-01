from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Case, DecimalField, Sum, Value, When
from django.db.models.functions import Coalesce

from categories.selectors import get_category_by_movement_type
from common.choices import MovementType
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
        paymente_method: Payment method used for the transaction.
        user: User that owns the transaction.
        category_id: Selected category ID.
        credit_card_id: Optional credit card ID for credit payments.
        subscription_id: Optional subscription ID when transaction come from a subscription.

    Raises:
        PermissionDenied: If user is missing.
        ValidationError: If category or model validation fails.

    Returns:
        The created transaction.
    """

    if user is None:
        raise PermissionDenied("You need to be authenticated to perform this action")

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


def calculate_current_balance(*, user) -> DecimalField:
    """
    Calculates the current balance, this function must be called after each
    transaction.

    Filters by User's Transactions and automatically calculates with all
    the transactions that the user owns.

    Args:
        user: current user that comes from request.user from the API.

    Returns:
        balance: The new current balance.
    """
    return Transaction.objects.filter(user=user).aggregate(
        balance=Coalesce(
            Sum(
                Case(
                    When(movement_type=MovementType.INCOME, then="amount"),
                    When(
                        movement_type=MovementType.EXPENSE,
                        then=Value(Decimal("-1.00")) * "amount",
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
            Decimal("0.00"),
        )
    )["balance"]


def deactivate_transaction(*, user, transaction_id: str) -> Transaction:
    """
    Soft-deletes a transaction by marking it as inactive (is_active=False).

    Args:
        user: The current user that comes from request.user from the API.
        transaction_id: The selected transaction id to deactivate.

    Raises:
        PermissionDenied: If the user is missing, the user not owns the selected
        transaction.
        ValidationError: If the selected transaction is already inactive, has the
        an active subscription.

    Returns:
        Transaction: the deactivated Transaction.
    """
    if user is None:
        raise PermissionDenied("You need to be authenticated to perform this action")

    # This update needs to be atomic to avoid data inconsistencies
    with transaction.atomic():
        selected_transaction = (
            Transaction.objects.select_related("subscription")
            .select_for_update()
            .get(id=transaction_id)
        )

        if selected_transaction.user != user:
            raise PermissionDenied("You cannot delete other user's transactions")

        if not selected_transaction.is_active:
            raise ValidationError({"transaction": "Transaction is already inactive"})

        if (
            selected_transaction.subscription
            and selected_transaction.subscription.is_active
        ):
            raise ValidationError(
                {
                    "transaction": "Transaction cannot be deleted because it has an active subscription"
                }
            )

        # Transactions are soft deleted to perserve the historical transactions data.
        selected_transaction.is_active = False
        selected_transaction.save(update_fields=["is_active", "updated_at"])

        return selected_transaction
