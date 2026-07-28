from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from categories.models import Category
from common.choices import PaymentMethod
from common.models import BaseModel
from credit_cards.models import CreditCard

# Create your models here.


class Subscription(BaseModel):
    class BillingCycle(models.TextChoices):
        YEARLY = "yearly", "Yearly"
        MONTHLY = "monthly", "Monthly"
        WEEKLY = "weekly", "Weekly"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="subscriptions",
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="subscriptions"
    )

    name = models.CharField(max_length=150)

    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices)
    next_payment_date = models.DateField()
    payment_method = models.CharField(max_length=8, choices=PaymentMethod.choices)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.payment_method == PaymentMethod.CREDIT and not self.credit_card:
            raise ValidationError(
                {
                    "credit_card": "Credit card is required when payment method is credit."
                }
            )
