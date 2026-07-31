from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied
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
