from django.conf import settings
from django.urls import reverse

from celery import shared_task

from .models import Friendship
from .notifications import FriendRequestEmailNotification


@shared_task
def send_friend_request_notification(friend_request: Friendship) -> bool:
    """Send a mail with friend request to target user."""
    subject = f"New friend request from {friend_request.from_user.username}!"
    url = reverse("user-detail", kwargs={"pk": friend_request.from_user.pk})
    friend_request_url = f"{settings.APP_DOMAIN}{url}"

    return FriendRequestEmailNotification(
        subject=subject,
        recipient_list=[friend_request.to_user.email],
        friend_request_url=friend_request_url,
    ).send()
