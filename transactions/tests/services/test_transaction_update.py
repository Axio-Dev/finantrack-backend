from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError

from categories.factories import create_category
from common.choices import MovementType, PaymentMethod
from subscriptions.factories import subscription
from transactions.factories import transaction
from transactions.services import update_transaction
from users.factories import create_user


@pytest.mark.django_db
class TestUpdateTransaction:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category(
            name="Salary",
            movement_type=MovementType.INCOME,
        )
        self.transaction = transaction(
            user=self.user,
            category=self.category,
            payment_method=PaymentMethod.CASH,
        )

    def test_updates_allowed_fields(self):
        data = {
            "name": "Freelance payment",
            "description": "Landing page work",
            "amount": Decimal("1200.00"),
            "transaction_date": date(2026, 8, 15),
        }

        updated_transaction = update_transaction(
            user=self.user,
            transaction_id=self.transaction.id,
            data=data,
        )

        updated_transaction.refresh_from_db()

        assert updated_transaction.name == data["name"]
        assert updated_transaction.description == data["description"]
        assert updated_transaction.amount == data["amount"]
        assert updated_transaction.transaction_date == data["transaction_date"]
        assert updated_transaction.user_id == self.user.id
        assert updated_transaction.category_id == self.category.id
        assert updated_transaction.movement_type == MovementType.INCOME
        assert updated_transaction.payment_method == PaymentMethod.CASH

    def test_updates_category_when_it_matches_transaction_movement_type(self):
        new_category = create_category(
            name="Bonus",
            movement_type=MovementType.INCOME,
        )

        updated_transaction = update_transaction(
            user=self.user,
            transaction_id=self.transaction.id,
            data={"category_id": new_category.id},
        )

        updated_transaction.refresh_from_db()

        assert updated_transaction.category_id == new_category.id

    def test_ignores_fields_that_are_not_allowed_to_be_updated(self):
        update_transaction(
            user=self.user,
            transaction_id=self.transaction.id,
            data={
                "movement_type": MovementType.EXPENSE,
                "payment_method": PaymentMethod.CREDIT,
            },
        )

        self.transaction.refresh_from_db()

        assert self.transaction.movement_type == MovementType.INCOME
        assert self.transaction.payment_method == PaymentMethod.CASH

    def test_without_user_raises_permission_denied(self):
        with pytest.raises(PermissionDenied) as error:
            update_transaction(
                user=None,
                transaction_id=self.transaction.id,
                data={"name": "Updated name"},
            )

        assert (
            str(error.value) == "You need to be authenticated to perform this action."
        )

    def test_anonymous_user_raises_permission_denied(self):
        with pytest.raises(PermissionDenied) as error:
            update_transaction(
                user=AnonymousUser(),
                transaction_id=self.transaction.id,
                data={"name": "Updated name"},
            )

        assert (
            str(error.value) == "You need to be authenticated to perform this action."
        )

    def test_inactive_transaction_raises_validation_error(self):
        self.transaction.is_active = False
        self.transaction.save(update_fields=["is_active"])

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=self.user,
                transaction_id=self.transaction.id,
                data={"name": "Updated name"},
            )

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }

    def test_transaction_from_another_user_raises_validation_error(self):
        another_user = create_user(email="anotheruser@test.com")

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=another_user,
                transaction_id=self.transaction.id,
                data={"name": "Updated name"},
            )

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }

    def test_subscription_transaction_raises_validation_error(self):
        related_subscription = subscription(
            user=self.user,
            category=self.category,
            payment_method=PaymentMethod.CASH,
        )
        self.transaction.subscription = related_subscription
        self.transaction.save(update_fields=["subscription"])

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=self.user,
                transaction_id=self.transaction.id,
                data={"name": "Updated name"},
            )

        assert error.value.message_dict == {
            "transaction": [
                "This transaction cannot be updated because it is linked to a subscription."
            ]
        }

    def test_category_that_does_not_match_movement_type_raises_validation_error(self):
        expense_category = create_category(
            name="Groceries",
            movement_type=MovementType.EXPENSE,
        )

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=self.user,
                transaction_id=self.transaction.id,
                data={"category_id": expense_category.id},
            )

        assert error.value.message_dict == {
            "category": [
                "Selected category does not exist or does not match with the selected movement type"
            ]
        }

    def test_invalid_amount_raises_validation_error(self):
        data = {
            "name": "Freelance payment",
            "description": "Landing page work",
            "amount": Decimal("0.00"),
            "transaction_date": date(2026, 8, 15),
        }

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=self.user, transaction_id=self.transaction.id, data=data
            )

        assert error.value.message_dict == {
            "amount": ["Ensure this value is greater than or equal to 0.01."]
        }

    def test_negative_amount_raises_validation_error(self):
        data = {
            "name": "Freelance payment",
            "description": "Landing page work",
            "amount": Decimal("-1.00"),
            "transaction_date": date(2026, 8, 15),
        }

        with pytest.raises(ValidationError) as error:
            update_transaction(
                user=self.user, transaction_id=self.transaction.id, data=data
            )

        assert error.value.message_dict == {
            "amount": ["Ensure this value is greater than or equal to 0.01."]
        }
