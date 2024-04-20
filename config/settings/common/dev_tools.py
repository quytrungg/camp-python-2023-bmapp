from .installed_apps import INSTALLED_APPS, LOCAL_APPS
from .middleware import MIDDLEWARE

# shell_plus configuration
# you can specify what additional libraries and blocks of
# code to be automatically imported when you run shell_plus
# command, in our case `inv django.shell`
# if you want factories to be included into your shell then you can do
# something like this
# *[("{}.factories".format(app), "*")
#   for app in LOCAL_APPS + TESTING_APPS]
# right inside SHELL_PLUS_PRE_IMPORTS

SHELL_PLUS = "ipython"
# what packages to preload inside shell plus
TOOLS_FOR_SHELL = [
    ("itertools", "*"),
    ("collections", "*"),
    ("datetime", "*"),
    "arrow",
    ("django.db.models.functions", "*"),
    ("django.db.models.expressions", "*"),
]
FACTORIES_FOR_SHELL = [
    f"from {app}.factories import *" for app in LOCAL_APPS
]
SHELL_PLUS_PRE_IMPORTS = (
    TOOLS_FOR_SHELL +
    FACTORIES_FOR_SHELL
)

# Print SQL Queries
SHELL_PLUS_PRINT_SQL = False

# Truncate sql queries to this number of characters (this is the default)
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

INSTALLED_APPS += (
    "debug_toolbar",
)

MIDDLEWARE = MIDDLEWARE + (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)


def _show_toolbar_callback(request) -> bool:
    """Show always debug toolbar for local/dev environ (exclude testing).

    So you do not have to set `INTERNAL_IPS`. It's a little pain with docker.

    """
    from django.conf import settings
    return not settings.TESTING


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": _show_toolbar_callback,
}
