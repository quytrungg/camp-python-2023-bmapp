from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

# register URL like
# router.register(r"users", UsersAPIView)
router = DefaultRouter()
router.register(r"", views.UsersViewSet, basename="user")

urlpatterns = [
    path("me", views.ProfileApiView.as_view(), name="profile"),
] + router.urls
