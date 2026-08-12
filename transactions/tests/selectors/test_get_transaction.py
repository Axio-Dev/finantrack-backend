import pytest
from django.core.exceptions import ValidationError

from categories.factories import create_category
from transactions.factories import transaction
from transactions.selectors import get_transaction
from users.factories import create_user


@pytest.mark.django_db
class TestGetTransaction:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category()
        self.transaction = transaction(user=self.user, category_id=self.category.id)

    def test_get_transaction_owned_by_user(self):
        valid_transaction = get_transaction(
            transaction_id=self.transaction.id, user=self.user
        )

        assert valid_transaction == self.transaction

    def test_non_existent_transaction_raises_validation_error(self):

        with pytest.raises(ValidationError) as error:
            get_transaction(
                transaction_id="00000000-0000-0000-0000-000000000000", user=self.user
            )

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }

    def test_try_to_get_antoher_users_transaction_raises_permission_denied(self):
        other_user = create_user(email="otheruser@test.com", password="otheruser123")
        other_transaction = transaction(user=other_user, category=self.category)

        with pytest.raises(ValidationError) as error:
            get_transaction(transaction_id=other_transaction.id, user=self.user)

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }

    def test_try_to_get_inactive_transaction_raises_validation_error(self):
        self.transaction.is_active = False
        self.transaction.save(update_fields=["is_active"])

        with pytest.raises(ValidationError) as error:
            get_transaction(transaction_id=self.transaction.id, user=self.user)

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }
