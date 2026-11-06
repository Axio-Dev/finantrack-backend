import pytest

from categories.factories import create_category
from common.choices import PaymentMethod
from transactions.factories import transaction
from transactions.selectors import list_transactions
from transactions.services import delete_transaction
from users.factories import create_user


@pytest.mark.django_db
class TestListTransactions:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category(name="Food with my girlfriend")
        self.transaction = transaction(
            user=self.user, category=self.category, payment_method=PaymentMethod.CASH
        )
        self.transaction2 = transaction(
            user=self.user, category=self.category, payment_method=PaymentMethod.CASH
        )

    def test_list_transactions_returns_all_user_transactions(self):
        transactions = list_transactions(user=self.user)

        assert set(transactions) == {self.transaction, self.transaction2}

    def test_list_transactions_returns_only_active_transactions(self):
        transaction3 = transaction(
            user=self.user, category=self.category, payment_method=PaymentMethod.CASH
        )

        delete_transaction(user=self.user, transaction_id=self.transaction2.id)

        transactions = list_transactions(user=self.user)

        assert set(transactions) == {self.transaction, transaction3}

    def test_list_transactions_returns_empty_queryset_when_user_has_no_transactions(
        self,
    ):
        user2 = create_user(
            email="user_with_no_transactions@test.com", password="test1234"
        )

        transactions = list_transactions(user=user2)

        assert not transactions.exists()
