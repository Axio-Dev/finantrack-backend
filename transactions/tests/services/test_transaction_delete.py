import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError

from categories.factories import create_category
from transactions.factories import transaction
from transactions.services import delete_transaction
from users.factories import create_user


@pytest.mark.django_db
class TestDeleteTransaction:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category()
        self.transaction = transaction(user=self.user, category_id=self.category.id)

    def test_soft_deletes_transaction(self):
        selected_transaction = self.transaction

        deactivated_transaction = delete_transaction(
            transaction_id=selected_transaction.id, user=selected_transaction.user
        )

        deactivated_transaction.refresh_from_db()

        assert deactivated_transaction.is_active is False

    def test_user_is_not_authenticated_raises_permission_denied(self):
        selected_transaction = self.transaction

        with pytest.raises(PermissionDenied) as error:
            delete_transaction(
                user=AnonymousUser(), transaction_id=selected_transaction.id
            )

        assert (
            str(error.value) == "You need to be authenticated to perform this action."
        )

    def test_deactivated_transaction_raises_validation_error(self):
        selected_transaction = self.transaction

        deactivated_transaction = delete_transaction(
            transaction_id=selected_transaction.id, user=selected_transaction.user
        )

        deactivated_transaction.refresh_from_db()

        assert deactivated_transaction.is_active is False

        with pytest.raises(ValidationError) as error:
            delete_transaction(
                transaction_id=deactivated_transaction.id,
                user=deactivated_transaction.user,
            )

        assert error.value.message_dict == {
            "transaction": ["Selected transaction does not exist or is inactive."]
        }
