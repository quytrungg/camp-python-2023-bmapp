from typing import Any

from django.db.models import Q
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.transactions.models import Category
from apps.users.models import User


def test_category_list_api(api_client: APIClient, normal_user: User) -> None:
    """Ensure that the category list view returns the correct data."""
    url = reverse("v1:category-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(
        Category.objects.filter(Q(user=normal_user) | Q(user__isnull=True)),
    )


def test_default_category_detail_api(
    api_client: APIClient,
    first_default_category: Category,
) -> None:
    """Ensure that any user can see the default categories."""
    url = reverse(
        "v1:category-detail",
        kwargs={"pk": first_default_category.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_user_defined_category_detail_api(
    api_client: APIClient,
    user_defined_category: Category,
) -> None:
    """Ensure that a user can see their own categories."""
    url = reverse(
        "v1:category-detail",
        kwargs={"pk": user_defined_category.pk},
    )
    response = api_client.get(url)
    assert Category.objects.filter(pk=user_defined_category.pk).exists()

    assert response.status_code == status.HTTP_200_OK


def test_not_owned_category_detail_api(
    another_api_client: APIClient,
    user_defined_category: Category,
) -> None:
    """Ensure that a user can't see another user's categories."""
    url = reverse(
        "v1:category-detail",
        kwargs={"pk": user_defined_category.pk},
    )
    response = another_api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthenticated_client(
    first_default_category: Category,
) -> None:
    """Ensure that unauthenticated user cannot see the categories."""
    url = reverse(
        "v1:category-detail",
        kwargs={"pk": first_default_category.pk},
    )
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_category_create_api(
    api_client: APIClient,
    normal_user: User,
    category_create_data: dict[str, Any],
) -> None:
    """Ensure that a user can create a category.

    There is no need to test the case that data for creating a category is
    invalid, because we only have 2 fields: one field is for the name, which is
    free text, and the other field is is_income, which is a binary field,
    and the frontend will take care of that.

    """
    url = reverse("v1:category-list")
    response = api_client.post(url, category_create_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(
        user=normal_user,
        **category_create_data,
    ).exists()


def test_category_update_api(
    api_client: APIClient,
    user_defined_category: Category,
    category_create_data: dict[str, Any],
) -> None:
    """Ensure that a user can update their own category.

    Make sure that the is_income field is not changed.

    """
    url = reverse(
        "v1:category-detail",
        kwargs={"pk": user_defined_category.pk},
    )
    category_create_data["is_income"] = not user_defined_category.is_income
    response = api_client.put(url, category_create_data)

    assert response.status_code == status.HTTP_200_OK
    assert Category.objects.filter(
        name=category_create_data["name"],
        user=user_defined_category.user,
    ).exists()

    user_defined_category.refresh_from_db()
    assert user_defined_category.is_income != category_create_data["is_income"]
