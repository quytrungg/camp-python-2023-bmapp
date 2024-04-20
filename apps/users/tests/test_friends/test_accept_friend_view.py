from django.test import Client
from django.urls import reverse

import pytest

from apps.users.factories import FriendshipFactory
from apps.users.models import Friendship, User


@pytest.fixture
def friend_request(from_user: User, to_user: User) -> Friendship:
    """Generate a friend request."""
    return FriendshipFactory(
        from_user=from_user,
        to_user=to_user,
    )


def test_accept_friend_view(
    to_client: Client,
    from_user: User,
    to_user: User,
    friend_request: Friendship,
) -> None:
    """Ensure AcceptFriendView works properly with status code 302.

    Response with 302 status code when user accepts a friend request from
    another user whom has or has not been friend.

    """
    response = to_client.get(
        reverse("accept-friend", kwargs={"request_id": friend_request.pk}),
    )

    assert response.status_code == 302
    friend_request.refresh_from_db()
    assert friend_request.accepted
    assert from_user.friends.filter(pk=to_user.pk).exists()

    another_response = to_client.get(
        reverse("accept-friend", kwargs={"request_id": friend_request.pk}),
    )

    assert another_response.status_code == 302


def test_accept_friend_view_invalid(
    from_client: User,
    friend_request: Friendship,
) -> None:
    """Restrict user who sent the friend request cannot accept but got 404."""
    response = from_client.get(
        reverse("accept-friend", kwargs={"request_id": friend_request.pk}),
    )

    assert response.status_code == 404
