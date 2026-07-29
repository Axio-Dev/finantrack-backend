from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from categories.models import Category


def category_deactivate(*, category_id: str, user) -> Category:
    """
    Soft-deletes a category by marking it as inactive.

    Args:
        category_id: ID of the category to deactivate.
        user: User requesting the deactivation.

    Raises:
        ValidationError: If the category is global, already inactive,
        has transactions, or has subscriptions.
        Category.DoesNotExist: If the category does not exist.
        PermissionDenied: If the User is None (not authtenticated),
        is not staff, is no the owner of the category (we're not
        allowing the creation of categories so far)

    Returns:
        Category: The deactivated category.
    """

    with transaction.atomic():
        category = Category.objects.select_for_update().get(id=category_id)

        if user is None:
            raise PermissionDenied("Authentication is required")

        if category.user is None and not user.is_staff:
            raise PermissionDenied("Global categories cannot be deleted by users.")

        if category.user is not None and category.user != user and not user.is_staff:
            raise PermissionDenied(
                "You don't have the permissions to delete this category"
            )

        if not category.is_active:
            raise ValidationError({"category": "Category is already inactive"})

        if category.transactions.exists():
            raise ValidationError(
                {
                    "category": (
                        "This category cannot be deleted because it has transactions."
                    )
                }
            )

        if category.subscriptions.exists():
            raise ValidationError(
                {
                    "category": (
                        "This category cannot be deleted because it has subscriptions"
                    )
                }
            )

        # Categories are soft-deleted to preserve historical transaction data.
        category.is_active = False
        category.save(update_fields=["is_active", "updated_at"])

        return category
