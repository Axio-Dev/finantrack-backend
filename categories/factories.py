from categories.models import Category
from common.choices import MovementType


def create_category(**kwargs):
    data = {
        "name": "Food",
        "movement_type": MovementType.EXPENSE,
        "user": None,
    }

    data.update(kwargs)

    return Category.objects.create(**data)
