from django.conf import settings
from django.utils import timezone

from config.celery import app
from libs.notifications.email import DefaultEmailNotification

from apps.transactions.models import Transaction
from apps.users.models import User


@app.task
def generate_admin_weekly_report() -> None:
    """Generate weekly report for Admin.

    The weekly report includes:
        - Total number of transactions made by users.
        - Total number of categories used by users.
        - Total number of new users.

    """
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    new_users = User.objects.filter(
        created__range=[start_date, end_date],
    ).values_list("username", flat=True)
    transactions = Transaction.objects.filter(
        created__range=(start_date, end_date),
    ).select_related("category")

    total_transactions = transactions.count()
    total_category_used = transactions.values("category").distinct().count()

    report_email = DefaultEmailNotification(
        subject="Admin Weekly Report",
        from_email=settings.SERVER_EMAIL,
        recipient_list=User.objects.filter(
            is_staff=True,
        ).values_list("email", flat=True),
        template="transactions/emails/admin_weekly_report.html",
        new_users=new_users,
        total_transactions=total_transactions,
        total_category_used=total_category_used,
    )
    report_email.send()
