from django.conf import settings
from django.db import models

from common.choices import MovementType
from common.models import BaseModel

# Create your models here.


class Category(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        blank=True,
        null=True,
    )

    title = models.CharField(max_length=150, unique=True)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
