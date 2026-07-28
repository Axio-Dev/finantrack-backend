from django.db import models


class MovementType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"
