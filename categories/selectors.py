from django.core.exceptions import ValidationError

from categories.models import Category


def get_category_by_movement_type(*, category_id: str, movement_type: str) -> Category:

    category = Category.objects.filter(
        id=category_id,
        movement_type=movement_type,
        user__isnull=True,
    ).first()

    if category is None:
        raise ValidationError(
            {
                "category": "Selected category does not exist or does not match with the selected movement type"
            }
        )

    return category
