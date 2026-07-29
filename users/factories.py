from users.models import User


def create_user(**kwargs):
    data = {
        "email": "testuser@test.com",
        "password": "Imtestingpassword1234",
    }

    data.update(kwargs)

    return User.objects.create_user(**data)
