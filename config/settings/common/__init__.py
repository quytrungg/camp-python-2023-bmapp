# -----------------------------------------------------------------------------
# General Django Configuration Starts Here
# -----------------------------------------------------------------------------
from .authentication import *
from .cache import *
from .celery import *
from .databases import *
from .drf import *
from .installed_apps import *
from .internationalization import *
from .logging import *
from .middleware import *
from .paths import *
from .security import *
from .static import *
from .storage import *
from .templates import *

# -----------------------------------------------------------------------------
# Business Logic Custom Variables and Settings
# -----------------------------------------------------------------------------
from .business_logic import *

APPEND_SLASH = False
SITE_ID = 1
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

ADMINS = (
    ("PhuongPham", "phuong.pham@saritasa.com"),
)

MANAGERS = ADMINS
TESTING = False
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Custom settings
APP_LABEL = "camp-python-2023-bmapp"

# a password URL for a frontend page; sent in a reset email
NEW_PASSWORD_URL = "TODO"
