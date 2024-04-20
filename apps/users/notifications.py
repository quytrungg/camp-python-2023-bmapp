from django.conf import settings
from django.utils.translation import gettext_lazy as _

from libs.notifications.email import DefaultEmailNotification


class UserPasswordResetEmailNotification(DefaultEmailNotification):
    """Used to send email with password reset link."""

    subject = _("Password Reset")
    template = "users/emails/password_reset.html"

    def __init__(self, user, **template_context):
        super().__init__(**template_context)
        self.user = user

    def get_recipient_list(self):
        """Get email's recipients."""
        return [self.user.email]

    def get_template_context(self):
        """Get email's template context."""
        self.template_context.update(
            new_password_url=settings.FRONTEND_URL + settings.NEW_PASSWORD_URL,
            app_url=settings.FRONTEND_URL,
            app_label=settings.APP_LABEL,
        )
        return self.template_context


class FriendRequestEmailNotification(DefaultEmailNotification):
    """Send an email notification of a friend request to target user."""

    template = "users/emails/friend_request.html"


class SharedBillEmailNotification(DefaultEmailNotification):
    """Send an email notification to friends tagged in a transaction."""

    template = "transactions/emails/shared_bill_notification.html"
