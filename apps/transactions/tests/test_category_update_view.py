from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.transactions.factories import CategoryFactory
from apps.transactions.models import Category


@pytest.fixture
def category(normal_user) -> Category:
    """Create a user-defined category for normal_user."""
    return CategoryFactory(user=normal_user)


@pytest.fixture
def updated_category_data() -> dict[str, Any]:
    """Provide data for updating category."""
    return {
        "name": "Modified name",
    }


def test_category_update_view(
    auth_client: Client,
    category: Category,
    updated_category_data: dict[str, Any],
) -> None:
    """Ensure user can only update their own category."""
    url = reverse("category-update", kwargs={"pk": category.pk})
    response = auth_client.post(url, updated_category_data)
    category.refresh_from_db()
    assert response.status_code == 302
    assert category.name == updated_category_data["name"]


def test_update_system_category(
    auth_client: Client,
    updated_category_data: dict[str, Any],
) -> None:
    """Ensure that user cannot update a default category."""
    default_category = Category.objects.filter(user__isnull=True)[0]
    url = reverse("category-update", kwargs={"pk": default_category.pk})
    response = auth_client.post(url, updated_category_data, follow=True)
    assert response.status_code == 404


def test_update_other_user_category(
    category: Category,
    updated_category_data: dict[str, Any],
    another_client: Client,
) -> None:
    """Ensure that a user cannot update other user's category."""
    url = reverse("category-update", kwargs={"pk": category.pk})

    response = another_client.post(url, updated_category_data, follow=True)
    assert response.status_code == 404
