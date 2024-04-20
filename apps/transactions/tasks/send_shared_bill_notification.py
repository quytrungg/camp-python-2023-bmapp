from django.db.models import QuerySet

from celery import shared_task

from apps.transactions.models import Transaction
from apps.users.models import User
from apps.users.notifications import SharedBillEmailNotification


@shared_task
def send_shared_bill_notification(
    user: User,
    friends: QuerySet,
    transaction: Transaction,
) -> None:
    """Send a mail notification about a shared bill transaction to users."""
    subject = f"You were tagged in a transaction by {user.username}!"

    for friend in friends:
        email = SharedBillEmailNotification(
            subject=subject,
            recipient_list=[friend.email],
            transaction=transaction,
            username=friend.username,
        )
        email.send()
