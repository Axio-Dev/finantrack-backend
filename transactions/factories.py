import datetime
from decimal import Decimal

from common.choices import MovementType, PaymentMethod
from transactions.models import Transaction


def transaction(**kwargs) -> Transaction:
    data = {
        "name": "Test Transaction 1",
        "description": "This a test description",
        "amount": Decimal("100.00"),
        "movement_type": MovementType.INCOME,
        "payment_method": PaymentMethod.CREDIT,
        "transaction_date": datetime.date(2026, 8, 2),
        "user": None,
        "category": None,
    }

    data.update(kwargs)

    return Transaction.objects.create(**data)
