from rest_framework.routers import DefaultRouter

from .views import ExchangeRateViewSet

router = DefaultRouter()
router.register(r"", ExchangeRateViewSet, basename="exchange-rate")
urlpatterns = router.urls
