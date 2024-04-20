from django.test import Client
from django.urls import reverse

import pytest
from pytest_lazyfixture import lazy_fixture

from apps.transactions.models import Category


@pytest.mark.parametrize(
    ["category", "expected"],
    [
        [
            lazy_fixture("first_default_category"),
            200,
        ],
        [
            lazy_fixture("user_defined_category"),
            200,
        ],
    ],
)
def test_for_available_category_detail_view(
    auth_client: Client,
    category: int,
    expected: int,
) -> None:
    """Ensure what category detail view is accessible."""
    url = reverse("category-detail", kwargs={"pk": category.pk})
    response = auth_client.get(url)

    assert response.status_code == expected


def test_not_own_category_detail_view(
    user_defined_category: Category,
    another_client: Client,
) -> None:
    """Ensure that a user can't see the detail of other's defined category."""
    url = reverse("category-detail", kwargs={"pk": user_defined_category.pk})
    response = another_client.get(url)

    assert response.status_code == 404
