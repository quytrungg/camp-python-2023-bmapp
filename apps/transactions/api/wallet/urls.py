from rest_framework.routers import DefaultRouter

from .views import WalletViewSet

router = DefaultRouter()
router.register(r"", WalletViewSet, basename="wallet")
urlpatterns = router.urls
