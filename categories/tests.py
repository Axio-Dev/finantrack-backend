import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from categories.factories import create_category
from categories.services import category_deactivate
from users.factories import create_user

# Create your tests here.


@pytest.mark.django_db
class TestCategoryDeactivate:
    def setup_method(self):
        self.user = create_user()
        self.category = create_category(user=self.user)
        self.global_category = create_category(name="Streaming")

    def test_cannot_deactivate_global_category_if_user_is_none(self):
        category = self.global_category

        with pytest.raises(PermissionDenied):
            category_deactivate(category_id=self.global_category.id, user=None)

        category.refresh_from_db()

        assert category.is_active is True

    def test_deactivate_user_category(self):
        category_deactivate(category_id=self.category.id, user=self.user)

        self.category.refresh_from_db()

        assert self.category.is_active is False

    def test_cannot_deactivate_global_category_as_regular_user(self):
        category = self.global_category

        with pytest.raises(ValidationError):
            category_deactivate(category_id=category.id, user=self.user)

        category.refresh_from_db()

        assert category.is_active is True
