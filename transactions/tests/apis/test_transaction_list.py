import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

from categories.factories import create_category
from common.choices import MovementType, PaymentMethod
from transactions.factories import transaction
from users.factories import create_user


@pytest.mark.django_db
class TestTransactionListApi(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.category = create_category(
            name="Salary",
            movement_type=MovementType.INCOME,
        )
        self.transaction = transaction(
            user=self.user, category=self.category, payment_method=PaymentMethod.CASH
        )
        self.url = reverse("transaction-list")

    def test_get_transaction_list_returns_200_ok(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(self.transaction.id),
                "name": self.transaction.name,
                "amount": str(self.transaction.amount),
            }
        ]
