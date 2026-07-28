from django.db import models


class MovementType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"
