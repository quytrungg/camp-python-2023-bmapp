from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.transactions.constants import NORMAL_USER_LIMITS
from apps.transactions.factories import CategoryFactory
from apps.transactions.models import Category
from apps.users.models import User


@pytest.fixture
def categories(normal_user: User) -> list[Category]:
    """Create a batch of categories.

    The number of categories created is 1 less than the limit to test the limit
    categories that a normal user can create. All limitations are defined in
    `NORMAL_USER_LIMITS` dictionary.

    """
    return CategoryFactory.create_batch(
        NORMAL_USER_LIMITS["max_custom_category_count"],
        user=normal_user,
    )


def test_category_create_view(
    auth_client: Client,
    normal_user: User,
    category_create_data: dict[str, Any],
) -> None:
    """Ensure users can create a new category under the limit.

    Users are allowed to create a new category if their number of custom
    categories are less than the limit number for normal user.

    """
    response = auth_client.post(
        reverse("category-create"),
        category_create_data,
    )

    assert response.status_code == 302
    assert Category.objects.filter(
        **category_create_data,
        user=normal_user,
    ).exists()


def test_category_create_view_limit(
    auth_client: Client,
    normal_user: User,
    category_create_data: dict[str, Any],
    categories: list[Category],
) -> None:
    """Ensure normal users cannot create a new category cross the limit.

    Users are not allowed to create a new category if their number of custom
    categories are equal or more than the limit number for normal user.

    """
    response = auth_client.post(
        reverse("category-create"),
        category_create_data,
    )

    assert response.status_code == 200
    assert not Category.objects.filter(
        **category_create_data,
        user=normal_user,
    ).exists()
    assert Category.objects.filter(
        user=normal_user,
    ).count() == NORMAL_USER_LIMITS["max_custom_category_count"]


def test_category_create_view_premium(
    auth_client: Client,
    normal_user: User,
    category_create_data: Category,
    categories: list[Category],
) -> None:
    """Ensure a premium user can create unlimited custom categories."""
    normal_user.is_premium = True
    normal_user.save()

    response = auth_client.post(
        reverse("category-create"),
        category_create_data,
    )

    assert response.status_code == 302
    assert Category.objects.filter(
        **category_create_data,
        user=normal_user,
    ).exists()
