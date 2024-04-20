from django.test import Client
from django.urls import reverse

import pytest

from apps.users.factories import FriendshipFactory
from apps.users.models import Friendship, User


@pytest.fixture
def friend_request_accepted(
    from_user: User,
    to_user: User,
) -> Friendship:
    """Generate an accepted friend request."""
    return FriendshipFactory(
        from_user=from_user,
        to_user=to_user,
        accepted=True,
    )


def test_remove_friend_view(
    from_client: Client,
    from_user: User,
    to_user: User,
    friend_request_accepted: Friendship,
) -> None:
    """Ensure RemoveFriendView works properly with status code 302.

    Response with 302 status code when user removes a friend request from
    another user whom has or has not been friend.

    """
    from_user.friends.add(to_user)

    response = from_client.get(
        reverse("remove-friend", kwargs={"user_id": to_user.pk}),
    )
    assert response.status_code == 302
    assert not from_user.friends.filter(pk=to_user.pk).exists()

    another_response = from_client.get(
        reverse("remove-friend", kwargs={"user_id": to_user.pk}),
    )
    assert another_response.status_code == 302


def test_remove_friend_view_invalid(
    from_client: Client,
    from_user: User,
    friend_request_accepted: Friendship,
) -> None:
    """Ensure users cannot remove themselves as friend and got 404 error."""
    response = from_client.get(
        reverse("remove-friend", kwargs={"user_id": from_user.pk}),
    )

    assert response.status_code == 404
