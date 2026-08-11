from decimal import Decimal

from credit_cards.models import CreditCard


def credit_card(**kwargs):
    data = {
        "user": None,
        "name": "Test credit card",
        "issuer": "My bank",
        "last_four_digits": "1234",
        "credit_limit": Decimal(80000),
        "closing_day": 19,
        "payment_due_day": 31,
    }

    data.update(kwargs)

    return CreditCard.objects.create(**data)
