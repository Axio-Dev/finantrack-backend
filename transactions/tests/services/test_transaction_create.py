from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError

from categories.factories import create_category
from common.choices import MovementType, PaymentMethod
from credit_cards.factories import credit_card
from subscriptions.factories import subscription
from transactions.models import Transaction
from transactions.services import create_transaction
from users.factories import create_user


@pytest.fixture
def make_transaction_data():
    def _make_transaction_data(**kwargs):
        data = {
            "name": "Cinema day",
            "description": "Hang out to the cinema with my friends",
            "movement_type": MovementType.EXPENSE,
            "transaction_date": date(2026, 8, 2),
            "amount": Decimal("200.00"),
            "payment_method": PaymentMethod.CASH,
            "credit_card_id": None,
            "subscription_id": None,
        }

        data.update(kwargs)

        return data

    return _make_transaction_data


def assert_transaction_matches_data(transaction_obj, data):
    assert Transaction.objects.filter(id=transaction_obj.id).exists()

    assert transaction_obj.user_id == data["user"].id
    assert transaction_obj.category_id == data["category_id"]
    assert transaction_obj.name == data["name"]
    assert transaction_obj.description == data["description"]
    assert transaction_obj.movement_type == data["movement_type"]
    assert transaction_obj.transaction_date == data["transaction_date"]
    assert transaction_obj.amount == data["amount"]
    assert transaction_obj.payment_method == data["payment_method"]
    assert transaction_obj.credit_card_id == data["credit_card_id"]
    assert transaction_obj.subscription_id == data["subscription_id"]


@pytest.mark.django_db
class TestCreateTransaction:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category(
            name="cinema",
            movement_type=MovementType.EXPENSE,
        )

    def test_creates_cash_transaction(self, make_transaction_data):

        data = make_transaction_data(user=self.user, category_id=self.category.id)

        transaction_obj = create_transaction(**data)

        transaction_obj.refresh_from_db()

        assert_transaction_matches_data(transaction_obj, data)

    def test_creates_debit_transaction(self, make_transaction_data):

        data = make_transaction_data(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.DEBIT,
        )

        transaction_obj = create_transaction(**data)

        transaction_obj.refresh_from_db()

        assert_transaction_matches_data(transaction_obj, data)

    def test_creates_credit_transaction(self, make_transaction_data):
        related_credit_card = credit_card(user=self.user)

        data = make_transaction_data(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.CREDIT,
            credit_card_id=related_credit_card.id,
        )

        transaction_obj = create_transaction(**data)

        transaction_obj.refresh_from_db()

        assert_transaction_matches_data(transaction_obj, data)

    def test_creates_transaction_with_subscription(self, make_transaction_data):

        related_credit_card = credit_card(user=self.user)

        related_subscription = subscription(
            user=self.user,
            category=self.category,
            payment_method=PaymentMethod.CREDIT,
            credit_card=related_credit_card,
        )

        data = make_transaction_data(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.CREDIT,
            credit_card_id=related_credit_card.id,
            subscription_id=related_subscription.id,
        )

        transaction_obj = create_transaction(**data)

        transaction_obj.refresh_from_db()

        assert_transaction_matches_data(transaction_obj, data)

    # Error tests

    def test_create_transaction_without_user_raises_permission_denied(
        self, make_transaction_data
    ):
        data = make_transaction_data(user=None, category_id=self.category.id)

        with pytest.raises(PermissionDenied) as error:
            create_transaction(**data)

        assert (
            str(error.value) == "You need to be authenticated to perform this action."
        )

    def test_create_transaction_with_anonymous_user_raises_permission_denied(
        self, make_transaction_data
    ):

        data = make_transaction_data(user=AnonymousUser(), category_id=self.category.id)

        with pytest.raises(PermissionDenied) as error:
            create_transaction(**data)

        assert (
            str(error.value) == "You need to be authenticated to perform this action."
        )

    def test_create_transaction_that_does_not_match_movement_type_raises_validation_error(
        self, make_transaction_data
    ):
        data = make_transaction_data(
            user=self.user,
            category_id=self.category.id,
            movement_type=MovementType.INCOME,
        )

        with pytest.raises(ValidationError) as error:
            create_transaction(**data)

        assert error.value.message_dict == {
            "category": [
                "Selected category does not exist or does not match with the selected movement type"
            ]
        }

    def test_create_transaction_without_category_raises_validation_error(
        self, make_transaction_data
    ):

        data = make_transaction_data(
            user=self.user,
            category_id=None,
        )

        with pytest.raises(ValidationError) as error:
            create_transaction(**data)

        assert error.value.message_dict == {
            "category": [
                "Selected category does not exist or does not match with the selected movement type"
            ]
        }

    def test_create_credit_transaction_without_credit_card_raises_validation_error(
        self, make_transaction_data
    ):

        data = make_transaction_data(
            user=self.user,
            category_id=self.category.id,
            payment_method=PaymentMethod.CREDIT,
            credit_card_id=None,
        )

        with pytest.raises(ValidationError) as error:
            create_transaction(**data)

        assert error.value.message_dict == {
            "credit_card": ["Credit card is required when payment method is credit."]
        }
