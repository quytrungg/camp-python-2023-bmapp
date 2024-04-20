from django.test import Client
from django.urls import reverse

import pytest
from pytest_lazyfixture import lazy_fixture

from apps.users.models import User


@pytest.mark.parametrize(
    "user",
    [
        lazy_fixture("normal_user"),
        lazy_fixture("another_user"),
    ],
)
def test_user_detail_view(auth_client: Client, user: User) -> None:
    """Ensure User detail page works properly with status code 200."""
    response = auth_client.get(
        reverse("user-detail", kwargs={"pk": user.pk}),
    )

    assert response.status_code == 200
