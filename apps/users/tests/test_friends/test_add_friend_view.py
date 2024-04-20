from django.test import Client
from django.urls import reverse

from apps.users.models import User


def test_add_friend_view(auth_client: Client, to_user: User) -> None:
    """Ensure AddFriendView works properly with status code 302.

    Response with 302 status code when user sends a friend request to another
    user whom has or has not been friend.

    """
    response = auth_client.get(
        reverse("add-friend", kwargs={"user_id": to_user.pk}),
    )
    another_response = auth_client.get(
        reverse("add-friend", kwargs={"user_id": to_user.pk}),
    )

    assert response.status_code == 302
    assert another_response.status_code == 302


def test_add_friend_view_invalid(
    auth_client: Client,
    from_user: User,
) -> None:
    """Ensure user cannot send a friend request to themselves."""
    response = auth_client.get(
        reverse("add-friend", kwargs={"user_id": from_user.pk}),
    )

    assert response.status_code == 404
