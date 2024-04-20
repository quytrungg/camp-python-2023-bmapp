from django.test import Client
from django.urls import reverse

from apps.users.factories import UserFactory
from apps.users.models import User


def test_friend_list_view(auth_client: Client, normal_user: User) -> None:
    """Ensure Friend list page works properly with status code 200."""
    normal_user.friends.add(UserFactory())
    response = auth_client.get(reverse("friend-list"))

    assert response.status_code == 200
    response_friends = response.context_data["users"]
    db_friends = User.objects.get(
        pk=normal_user.pk,
    ).friends.all()[:response.context_data["paginate_by"]]
    assert response_friends.exists()
    assert list(response_friends) == list(db_friends)
