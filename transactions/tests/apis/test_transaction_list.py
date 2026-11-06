import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

from categories.factories import create_category
from common.choices import MovementType, PaymentMethod
from transactions.factories import transaction
from transactions.services import delete_transaction
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
        self.transaction2 = transaction(
            user=self.user, category=self.category, payment_method=PaymentMethod.CASH
        )
        self.url = reverse("transaction-list")

    def test_transaction_list_returns_all_user_transactions(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(self.transaction.id),
                "name": self.transaction.name,
                "amount": str(self.transaction.amount),
            },
            {
                "id": str(self.transaction2.id),
                "name": self.transaction2.name,
                "amount": str(self.transaction2.amount),
            },
        ]

    def test_transaction_list_returns_an_empty_list_when_user_has_no_transactions(
        self,
    ):
        user2 = create_user(
            email="no_transactions_user@test.com", password="testing123"
        )
        self.client.force_authenticate(user=user2)

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.json() == []

    def test_transaction_list_returns_403_when_user_is_not_authenticated(
        self,
    ):
        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 403
        assert data == {"detail": "Authentication credentials were not provided."}

    def test_transaction_list_excludes_other_users_transactions(
        self,
    ):
        other_user = create_user(email="otheruser@test.com", password="otheruser1234")
        transaction(
            user=other_user,
            category=self.category,
            payment_method=PaymentMethod.CASH,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 200
        assert {item["id"] for item in data} == {
            str(self.transaction.id),
            str(self.transaction2.id),
        }
        assert len(data) == 2

    def test_transaction_list_returns_only_active_transactions(self):
        delete_transaction(user=self.user, transaction_id=self.transaction2.id)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 200
        assert [item["id"] for item in data] == [str(self.transaction.id)]
        assert len(data) == 1

    def test_transaction_list_returns_an_empty_list_when_user_has_only_deactivated_transactions(
        self,
    ):
        delete_transaction(user=self.user, transaction_id=self.transaction.id)
        delete_transaction(user=self.user, transaction_id=self.transaction2.id)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        data = response.json()

        assert response.status_code == 200
        assert data == []
