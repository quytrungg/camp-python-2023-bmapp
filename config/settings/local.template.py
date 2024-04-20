# pylint: skip-file
# flake8: noqa
import socket
import sys

from .common import *

FRONTEND_URL = "home/"
APP_DOMAIN = "0.0.0.0:8000"
ENVIRONMENT = "local"
DEBUG = True

# Import dev tools only when DEBUG enable
if DEBUG:
    from .common.dev_tools import *

# disable django DEBUG if we run celery worker
if "celery" in sys.argv[0]:
    DEBUG = False

INTERNAL_IPS = (
    "0.0.0.0",
    "127.0.0.1",
)
# Hack to have working `debug` context processor when developing with docker
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += (ip[:-1] + "1",)

DATABASES["default"].update(
    NAME="camp-python-2023-bmapp-dev",
    USER="camp-python-2023-bmapp-user",
    PASSWORD="manager",
    HOST="postgres",
    PORT="5432",
    CONN_MAX_AGE=0,
)

# Don't use celery when you're local
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_ROUTES = {}
CELERY_BROKER_URL = "redis://redis/1"
CELERY_RESULT_BACKEND = "redis://redis/1"
CELERY_TASK_DEFAULT_QUEUE = "development"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@camp-python-2023-bmapp.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

CACHES["default"].update(
    LOCATION="redis://redis/1",
)

MIDDLEWARE += (
    "corsheaders.middleware.CorsMiddleware",
)

INSTALLED_APPS += (
    'django_probes',  # wait for DB to be ready to accept connections
    "corsheaders",    # provide CORS for local development
)

# Provide CORS for local development
# This is necessary when developer wants to run the frontend application
# locally and communicate with the local backend server. This does not affect
# django applications with their own frontend or mobile APIs
# see doc here
# https://github.com/ottoyiu/django-cors-headers/
CORS_ORIGIN_ALLOW_ALL = False
# Custom headers
CORS_EXPOSE_HEADERS = ()
CORS_ALLOW_HEADERS = (
    "x-requested-with",
    "content-type",
    "accept",
    "origin",
    "authorization",
    "x-csrftoken",
    "user-agent",
    "accept-encoding",
)
