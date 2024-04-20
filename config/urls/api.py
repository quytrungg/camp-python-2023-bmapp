from django.urls import include, path

app_name = "api"


urlpatterns = [
    # API URLS
    path("users/", include("apps.users.api.urls")),
    path("auth/", include("apps.users.api.auth.urls")),
    path("transactions/", include("apps.transactions.api.transactions.urls")),
    path("wallets/", include("apps.transactions.api.wallet.urls")),
    path("rates/", include("apps.rates.api.urls")),
    path("categories/", include("apps.transactions.api.category.urls")),
    path("home/", include("apps.transactions.api.home.urls")),
]
