from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.postgres.fields import CIEmailField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from imagekit import models as imagekitmodels
from imagekit.processors import ResizeToFill, Transpose

from apps.core.models import BaseModel
from apps.users import constants


class UserManager(DjangoUserManager):
    """Adjusted user manager that works with `username` field."""

    # pylint: disable=arguments-differ
    def _create_user(self, username, email, password, **extra_fields):
        """Create and save a user.

        Need to provide the username, email and password.

        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # pylint: disable=arguments-differ
    # pylint: disable=signature-differs
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create superuser instance (used by `createsuperuser` cmd)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(
    AbstractBaseUser,
    PermissionsMixin,
    BaseModel,
):
    """Custom user model with username.

    Attrs:
        username: username of the user, must be unique
        first_name: first name of the user
        last_name: last name of the user
        email: email of the user, must be unique
        phone_number: phone number of the user, must be unique
        date_of_birth: date of birth of the user
        is_premium: premium status of the user, default is False
        default_currency: default currency of the user, default is VND
        transaction_count: number of transactions of the user, default is 0
        transaction_streak: number of consecutive transactions of the user

    """

    username = models.CharField(
        verbose_name=_("Username"),
        max_length=30,
        unique=True,
    )

    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=30,
        blank=True,
    )

    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=30,
        blank=True,
    )

    email = CIEmailField(
        verbose_name=_("Email address"),
        max_length=254,  # to be compliant with RFCs 3696 and 5321
        unique=True,
    )

    phone_number = models.CharField(
        verbose_name=_("Phone number"),
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\+84[0-9]{9}$",
                message="Phone number must be in the format \"+84xxxxxxxxx\".",
            ),
        ],
        unique=True,
        default=constants.DEFAULT_PHONE_NUMBER,
    )

    date_of_birth = models.DateField(
        verbose_name=_("Date of birth"),
        null=True,
    )

    is_premium = models.BooleanField(
        verbose_name=_("Premium status"),
        default=False,
    )

    default_currency = models.CharField(
        verbose_name=_("Default currency"),
        max_length=3,
        default=constants.DEFAULT_CURRENCY,
    )

    transaction_count = models.IntegerField(
        verbose_name=_("Transaction count"),
        default=constants.DEFAULT_TRANSACTION_COUNT,
    )

    transaction_streak = models.IntegerField(
        verbose_name=_("Transaction streak"),
        default=constants.DEFAULT_TRANSACTION_STREAK,
    )

    is_staff = models.BooleanField(
        verbose_name=_("Staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site.",
        ),
    )

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active.",
        ),
    )

    avatar = imagekitmodels.ProcessedImageField(
        verbose_name=_("Avatar"),
        blank=True,
        null=True,
        upload_to=settings.DEFAULT_MEDIA_PATH,
        max_length=512,
        processors=[Transpose()],
        options={
            "quality": 100,
        },
    )

    avatar_thumbnail = imagekitmodels.ImageSpecField(
        source="avatar",
        processors=[
            ResizeToFill(50, 50),
        ],
    )

    friends = models.ManyToManyField(
        verbose_name=_("Friends"),
        to="self",
        through="Friendship",
        related_name="friends",
    )

    updated_information = models.BooleanField(
        verbose_name=_("Updated information"),
        default=False,
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [EMAIL_FIELD]

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.email


class Friendship(BaseModel):
    """Create model for Friendship.

    Attrs:
        from_user: user's id who intends to send a friend request.
        to_user: user's id whom will receive the friend request.
        accepted: boolean field to indicate whether the friend request is
        accepted.

    """

    from_user = models.ForeignKey(
        to=User,
        verbose_name=_("From user"),
        on_delete=models.CASCADE,
        related_name="friend_request_sender",
    )
    to_user = models.ForeignKey(
        to=User,
        verbose_name=_("To user"),
        on_delete=models.CASCADE,
        related_name="friend_request_receiver",
    )
    accepted = models.BooleanField(
        verbose_name=_("Accepted"),
        default=False,
    )

    class Meta:
        verbose_name = _("Friendship")
        verbose_name_plural = _("Friendships")

    def __str__(self) -> str:
        return f"Friend request from {self.from_user} to {self.to_user}"
