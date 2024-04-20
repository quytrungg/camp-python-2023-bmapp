from django.contrib import admin
from django.urls import include, path

from apps.core.views import IndexView
from apps.transactions.views import HomeView

from .api_versions import urlpatterns as api_urlpatterns
from .debug import urlpatterns as debug_urlpatterns

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path('accounts/', include('allauth.urls')),
    path("home/", HomeView.as_view(), name="home"),
    path("mission-control-center/", admin.site.urls),
    # Django Health Check url
    # See more details: https://pypi.org/project/django-health-check/
    # Custom checks at lib/health_checks
    path("health/", include("health_check.urls")),
    path("users/", include("apps.users.urls")),
    path("categories/", include("apps.transactions.urls.category")),
    path("wallets/", include("apps.transactions.urls.wallet")),
    path("transactions/", include("apps.transactions.urls.transaction")),
    path("rates/", include("apps.rates.urls")),
]

urlpatterns += api_urlpatterns
urlpatterns += debug_urlpatterns
