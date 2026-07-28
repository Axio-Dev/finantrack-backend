from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from categories.models import Category
from common.choices import MovementType, PaymentMethod
from common.models import BaseModel
from credit_cards.models import CreditCard
from subscriptions.models import Subscription

# Create your models here.


class Transaction(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="transactions"
    )
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.PROTECT,
        related_name="transactions",
        blank=True,
        null=True,
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        related_name="transactions",
        blank=True,
        null=True,
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    movement_type = models.CharField(max_length=8, choices=MovementType.choices)
    payment_method = models.CharField(max_length=8, choices=PaymentMethod.choices)

    transaction_date = models.DateField()

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.payment_method == PaymentMethod.CREDIT and not self.credit_card:
            raise ValidationError(
                {
                    "credit_card": "Credit card is required when payment method is credit."
                }
            )
