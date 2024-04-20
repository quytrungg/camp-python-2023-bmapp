import sys
import environ

from .common import *

env = environ.Env()

env.read_env()

DEBUG = env.bool("DEBUG", default=False)

ENVIRONMENT = env.str("ENVIRONMENT")

FRONTEND_URL = env.str("FRONTEND_URL", default="home/")

# ------------------------------------------------------------------------------
# DATABASES - PostgreSQL
# ------------------------------------------------------------------------------
DATABASES["default"].update(
    NAME=env.str("RDS_DB_NAME"),
    USER=env.str("RDS_DB_USER"),
    PASSWORD=env.str("RDS_DB_PASSWORD"),
    HOST=env.str("RDS_DB_HOST"),
    PORT=env.str("RDS_DB_PORT"),
)

# ------------------------------------------------------------------------------
# AWS S3 - Django Storages S3
# ------------------------------------------------------------------------------
AWS_STORAGE_BUCKET_NAME = env.str("AWS_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = env.str("AWS_S3_DIRECT_REGION")
AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_DEFAULT_ACL = "public-read"

# ------------------------------------------------------------------------------
# EMAIL SETTINGS
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env.int("EMAIL_HOST_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_HOST_USE_TLS")
DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL",
    "no-reply@camp-python-2023-bmapp.com",
)
SERVER_EMAIL = env.str("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

redis_host = env.str("REDIS_HOST")
redis_port = env.int("REDIS_PORT")
redis_db = env.int("REDIS_DB")

# ------------------------------------------------------------------------------
# CELERY
# ------------------------------------------------------------------------------
CELERY_TASK_DEFAULT_QUEUE = (
    f"{APP_LABEL.lower().replace(' ', '-')}-{ENVIRONMENT}"
)
CELERY_BROKER_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"
CELERY_RESULT_BACKEND = f"redis://{redis_host}:{redis_port}/{redis_db}"

# ------------------------------------------------------------------------------
# REDIS
# ------------------------------------------------------------------------------
# Setting needed for redis health check
REDIS_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"

CACHES["default"].update(
    LOCATION=REDIS_URL,
)
# ------------------------------------------------------------------------------
# DJANGO SECURITY
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# ------------------------------------------------------------------------------
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["*"]

# disable django DEBUG if we run celery worker
if "celery" in sys.argv[0]:
    DEBUG = False

if DEBUG:
    # Dev tools settings
    from .common.dev_tools import *
