"""Configuration file for pytest."""
from django.conf import settings
from django.test import Client

import pytest

from apps.rates.models import Currency
from apps.users.factories import UserFactory
from apps.users.models import User


def pytest_configure():
    """Set up Django settings for tests.

    `pytest` automatically calls this function once when tests are run.

    """
    settings.DEBUG = False
    settings.TESTING = True

    # The default password hasher is rather slow by design.
    # https://docs.djangoproject.com/en/dev/topics/testing/overview/
    settings.PASSWORD_HASHERS = (
        "django.contrib.auth.hashers.MD5PasswordHasher",
    )
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # To disable celery in tests
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture(scope="session", autouse=True)
def django_db_setup(django_db_setup):
    """Set up test db for testing."""


@pytest.fixture(autouse=True)
# pylint: disable=invalid-name
def enable_db_access_for_all_tests(django_db_setup, db):
    """Enable access to DB for all tests."""


@pytest.fixture(scope="session", autouse=True)
def temp_directory_for_media(tmpdir_factory):
    """Fixture that set temp directory for all media files.

    This fixture changes FILE_STORAGE to filesystem and provides temp dir for
    media. PyTest cleans up this temp dir by itself after few test runs

    """
    settings.DEFAULT_FILE_STORAGE = (
        "django.core.files.storage.FileSystemStorage"
    )
    media = tmpdir_factory.mktemp("tmp_media")
    settings.MEDIA_ROOT = media


@pytest.fixture(scope="session")
def first_currency(django_db_blocker) -> int:
    """Return the primary key of the first currency in the database."""
    with django_db_blocker.unblock():
        return Currency.objects.first()


@pytest.fixture(scope="session")
def last_currency(django_db_blocker) -> Currency:
    """Return the last currency in the database."""
    with django_db_blocker.unblock():
        return Currency.objects.last()


@pytest.fixture(scope="session")
def normal_user(django_db_blocker, first_currency: Currency) -> User:
    """Generate a test user as session and delete after yield."""
    with django_db_blocker.unblock():
        user = UserFactory()
        user.default_currency = Currency.objects.get(
            pk=first_currency.pk,
        ).code
        yield user
        user.delete()


@pytest.fixture(scope="session")
def another_user(django_db_blocker, first_currency: Currency) -> User:
    """Generate a test user as session and delete after yield."""
    with django_db_blocker.unblock():
        user = UserFactory()
        user.default_currency = Currency.objects.get(
            pk=first_currency.pk,
        ).code
        yield user
        user.delete()


@pytest.fixture(scope="session")
def auth_client(normal_user: User) -> Client:
    """Return authenticated client."""
    client = Client()
    client.force_login(normal_user)
    return client


@pytest.fixture(scope="session")
def another_client(another_user) -> Client:
    """Return another client."""
    client = Client()
    client.force_login(another_user)
    return client
