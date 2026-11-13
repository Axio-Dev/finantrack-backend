from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

from categories.factories import create_category
from common.choices import MovementType, PaymentMethod
from credit_cards.factories import credit_card
from transactions.models import Transaction
from users.factories import create_user


@pytest.mark.django_db
class TestTransactionCreateApi(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.category = create_category()
        self.payload = {
            "name": "Test transactions",
            "description": "Testing apis",
            "amount": Decimal("100.5"),
            "movement_type": MovementType.EXPENSE,
            "payment_method": PaymentMethod.CASH,
            "category_id": self.category.id,
            "transaction_date": date(2026, 11, 10),
        }
        self.url = reverse("transaction-create")

    def test_transaction_create_returns_201_and_transaction_data_when_payload_is_valid(
        self,
    ):
        self.client.force_authenticate(user=self.user)
        count_before = Transaction.objects.count()

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 201
        assert "id" in data, data
        assert data["name"] == self.payload["name"]
        assert Decimal(data["amount"]) == self.payload["amount"]

        created_transaction = Transaction.objects.get(pk=data["id"])

        assert Transaction.objects.count() == count_before + 1
        assert created_transaction.user_id == self.user.id
        assert created_transaction.name == self.payload["name"]
        assert created_transaction.description == self.payload["description"]
        assert created_transaction.amount == self.payload["amount"]
        assert created_transaction.category_id == self.payload["category_id"]
        assert created_transaction.transaction_date == self.payload["transaction_date"]
        assert created_transaction.movement_type == self.payload["movement_type"]
        assert created_transaction.payment_method == self.payload["payment_method"]

    def test_transaction_create_creates_transaction_when_description_is_none(self):
        self.client.force_authenticate(user=self.user)

        self.payload["description"] = None

        count_before = Transaction.objects.count()

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 201, data
        assert "id" in data, data

        created_transaction = Transaction.objects.get(pk=data["id"])

        assert Transaction.objects.count() == count_before + 1
        assert created_transaction.description == ""

    def test_transaction_create_creates_transaction_when_description_is_omitted(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        del self.payload["description"]

        count_before = Transaction.objects.count()

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 201, data
        assert "id" in data, data

        created_transaction = Transaction.objects.get(pk=data["id"])

        assert Transaction.objects.count() == count_before + 1
        assert created_transaction.description == ""

    def test_transaction_create_creates_transaction_when_description_is_empty(self):
        self.client.force_authenticate(user=self.user)

        self.payload["description"] = ""

        count_before = Transaction.objects.count()

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 201, data
        assert "id" in data, data

        created_transaction = Transaction.objects.get(pk=data["id"])

        assert Transaction.objects.count() == count_before + 1
        assert created_transaction.description == ""

    def test_transaction_create_returns_400_and_does_not_create_transaction_when_required_fields_are_missing(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        count_before = Transaction.objects.count()

        invalid_payload = {
            "name": "",
            "payment_method": PaymentMethod.CASH,
            "category_id": self.category.id,
            "transaction_date": date(2026, 11, 10),
        }

        response = self.client.post(self.url, data=invalid_payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "name": ["This field may not be blank."],
            "amount": ["This field is required."],
            "movement_type": ["This field is required."],
        }
        assert Transaction.objects.count() == count_before

    def test_transaction_create_returns_400_when_amount_is_zero(self):
        self.client.force_authenticate(user=self.user)

        self.payload["amount"] = "0.00"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "amount": ["Ensure this value is greater than or equal to 0.01."]
        }

    def test_transaction_create_returns_400_when_amount_is_negative(self):
        self.client.force_authenticate(user=self.user)

        self.payload["amount"] = "-1.00"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "amount": ["Ensure this value is greater than or equal to 0.01."]
        }

    def test_transaction_create_creates_transaction_when_amount_is_the_minimum_value(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        count_before = Transaction.objects.count()

        self.payload["amount"] = Decimal("0.01")

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 201
        assert "id" in data, data
        assert Transaction.objects.count() == count_before + 1

        created_transaction = Transaction.objects.get(pk=data["id"])

        assert created_transaction.amount == Decimal(data["amount"])
        assert Decimal(data["amount"]) == self.payload["amount"]

    def test_transaction_create_returns_400_when_payment_method_is_credit_and_credit_card_id_is_not_associated(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        self.payload["payment_method"] = PaymentMethod.CREDIT

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "credit_card": ["Credit card is required when payment method is credit."]
        }

    def test_transaction_create_returns_400_when_category_does_not_match_movement_type(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        self.payload["movement_type"] = MovementType.INCOME

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "category": [
                "Selected category does not exist or does not match with the selected movement type"
            ]
        }

    def test_transaction_create_returns_400_when_category_does_not_exist(self):
        self.client.force_authenticate(user=self.user)

        self.payload["category_id"] = "ea51b921-a6f7-4295-8995-2acb161cae5a"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "category": [
                "Selected category does not exist or does not match with the selected movement type"
            ]
        }

    def test_transaction_create_returns_400_when_payment_method_is_not_credit_and_credit_card_is_associated(
        self,
    ):
        self.client.force_authenticate(user=self.user)

        user_credit_card = credit_card(user=self.user)

        self.payload["payment_method"] = PaymentMethod.CASH
        self.payload["credit_card_id"] = user_credit_card.id

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "credit_card": [
                "A credit card can only be associated whtn the payment method is credit."
            ]
        }

    def test_transaction_create_returns_400_when_choices_are_invalid(self):
        self.client.force_authenticate(user=self.user)

        self.payload["payment_method"] = "invalid_method"
        self.payload["movement_type"] = "invalid_movement"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "payment_method": ['"invalid_method" is not a valid choice.'],
            "movement_type": ['"invalid_movement" is not a valid choice.'],
        }

    def test_transaction_create_returns_403_when_non_authenticated_user_creates_transaction(
        self,
    ):
        count_before = Transaction.objects.count()

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 403
        assert data == {"detail": "Authentication credentials were not provided."}
        assert count_before == Transaction.objects.count()

    def test_transaction_create_returns_400_when_transaction_date_format_is_wrong(self):
        self.client.force_authenticate(user=self.user)

        self.payload["transaction_date"] = "not-a-date"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        print(data)

        assert response.status_code == 400
        assert data == {
            "transaction_date": [
                "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
            ]
        }

    def test_transaction_create_returns_400_when_transaction_date_does_not_exist(self):
        self.client.force_authenticate(user=self.user)

        self.payload["transaction_date"] = "2026-02-30"

        response = self.client.post(self.url, data=self.payload, format="json")
        data = response.json()

        assert response.status_code == 400
        assert data == {
            "transaction_date": [
                "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
            ]
        }
