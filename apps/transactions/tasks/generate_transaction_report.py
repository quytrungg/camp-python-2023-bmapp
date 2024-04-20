from django.conf import settings
from django.utils import timezone

from config.celery import app
from libs.notifications.email import DefaultEmailNotification

from apps.transactions.models import Transaction
from apps.users.models import User


@app.task
def generate_transaction_report() -> None:
    """Generate transaction report.

    At the end of every week, generate a report about transactions of the week
    and send it to the user's email.

    """
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    for user in User.objects.all():
        transactions = Transaction.objects.filter(
            user=user,
            date__range=(start_date, end_date),
        )

        report_email = DefaultEmailNotification(
            subject="Transaction Report",
            from_email=settings.SERVER_EMAIL,
            recipient_list=[user.email],
            template="transactions/emails/weekly_report.html",
            username=user.username,
            transactions=transactions,
        )
        report_email.send()
