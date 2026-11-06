import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

from categories.factories import create_category
from common.choices import PaymentMethod
from transactions.factories import transaction
from transactions.services import delete_transaction
from users.factories import create_user


@pytest.mark.django_db
class TestTransactionDetailApi(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.category = create_category()
        self.transaction1 = transaction(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.CASH,
        )
        self.transaction2 = transaction(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.CASH,
        )
        self.url = reverse(
            "transaction-detail", kwargs={"transaction_id": self.transaction1.id}
        )

    def test_get_transaction_returns_user_transaction(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 200
        assert data == {
            "id": str(self.transaction1.id),
            "name": self.transaction1.name,
            "amount": str(self.transaction1.amount),
        }

    def test_transaction_detail_returns_404_when_transactions_is_inactive(
        self,
    ):
        self.client.force_authenticate(user=self.user)
        delete_transaction(user=self.user, transaction_id=self.transaction1.id)
        delete_transaction(user=self.user, transaction_id=self.transaction2.id)

        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 404
        assert data == {"detail": "Transaction not found."}

    def test_get_transaction_returns_403_wheh_user_is_not_authenticated(self):
        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 403
        assert data == {"detail": "Authentication credentials were not provided."}

    def test_transaction_detail_return_404_when_transaction_belongs_to_another_user(
        self,
    ):
        user2 = create_user(email="other_user@test.com", password="test1234")

        self.client.force_authenticate(user=user2)

        response = self.client.get(
            reverse(
                "transaction-detail", kwargs={"transaction_id": self.transaction1.id}
            )
        )
        data = response.json()

        assert response.status_code == 404
        assert data == {"detail": "Transaction not found."}
