from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from common.models import BaseModel

# Create your models here.


class CreditCard(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_cards"
    )

    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=50)
    last_four_digits = models.CharField(
        max_length=4,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^$|^\d{4}$",
                message="Last four digits must be empty or contain exactly 4 digits",
            )
        ],
    )

    credit_limit = models.DecimalField(max_digits=12, decimal_places=2)
    closing_day = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    payment_due_day = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )

    def __str__(self) -> str:
        return f"{self.name} ****{self.last_four_digits}"
