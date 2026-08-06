from datetime import date
from decimal import Decimal

from subscriptions.models import Subscription


def subscription(**kwargs):
    data = {
        "user": None,
        "credit_card": None,
        "category": None,
        "payment_method": None,
        "name": "Spotify",
        "amount": Decimal("189.99"),
        "billing_cycle": "monthly",
        "next_payment_date": date(2026, 8, 3),
    }

    data.update(**kwargs)

    return Subscription.objects.create(**data)
