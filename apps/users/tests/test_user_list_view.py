from django.test import Client
from django.urls import reverse

from apps.users.models import User


def test_user_list_view(auth_client: Client, normal_user: User) -> None:
    """Ensure User list page works properly with status code 200."""
    response = auth_client.get(reverse("user-list"))

    assert response.status_code == 200

    response_users = response.context_data["users"]
    db_users = User.objects.exclude(
        pk=normal_user.pk,
    )[:response.context_data["paginate_by"]]
    assert list(response_users) == list(db_users)
