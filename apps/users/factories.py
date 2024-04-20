import uuid

from django.conf import settings

import factory

from apps.users.models import Friendship

from . import models

DEFAULT_PASSWORD = "Test111!"


class UserFactory(factory.django.DjangoModelFactory):
    """Factory to generate test User instance."""

    username = factory.Faker("user_name")
    phone_number = factory.Sequence(lambda n: f"+84{n:09}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: f"+84{n:09}")

    avatar = factory.django.ImageField(color="magenta")
    password = factory.PostGenerationMethodCall(
        "set_password",
        DEFAULT_PASSWORD,
    )

    class Meta:
        model = models.User

    @factory.lazy_attribute
    def email(self):
        """Return formatted email."""
        return (
            f"{uuid.uuid4()}@"
            f"{settings.APP_LABEL.lower().replace(' ', '-')}.com"
        )


class AdminUserFactory(UserFactory):
    """Factory to generate test User model with admin's privileges."""

    is_superuser = True
    is_staff = True

    class Meta:
        model = models.User


class FriendshipFactory(factory.django.DjangoModelFactory):
    """Provide a factory class for Friendship model."""

    class Meta:
        model = Friendship
