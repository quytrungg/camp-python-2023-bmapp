from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    AcceptFriendView,
    AddFriendView,
    CancelFriendView,
    DeclineFriendView,
    FriendListView,
    RegisterView,
    RemoveFriendView,
    UserDetailView,
    UserFirstUpdateView,
    UserListView,
    UserLoginView,
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("friends/", FriendListView.as_view(), name="friend-list"),
    path(
        "login/",
        UserLoginView.as_view(
            template_name="users/auth/login.html",
            next_page="/",
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "first_time_update/",
        UserFirstUpdateView.as_view(),
        name="first-time-update",
    ),
    path(
        "add-friend/<int:user_id>/",
        AddFriendView.as_view(),
        name="add-friend",
    ),
    path(
        "cancel-friend/<int:user_id>",
        CancelFriendView.as_view(),
        name="cancel-friend",
    ),
    path(
        "accept-friend/<int:request_id>/",
        AcceptFriendView.as_view(),
        name="accept-friend",
    ),
    path(
        "decline-friend/<int:user_id>/",
        DeclineFriendView.as_view(),
        name="decline-friend",
    ),
    path(
        "remove-friend/<int:user_id>/",
        RemoveFriendView.as_view(),
        name="remove-friend",
    ),
]
