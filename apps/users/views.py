from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q, QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from apps.core.views import BaseListView
from apps.transactions.models import Wallet
from apps.users.forms import UserFirstUpdateForm, UserRegistrationForm
from apps.users.models import Friendship, User

from .filters import UserFilter
from .tasks import send_friend_request_notification


class UserLoginView(LoginView):
    """View for user login functionality.

    Custom the get_success_url to check for first time info update.

    """

    template_name = "users/auth/login.html"

    def get_success_url(self):
        """Get the success URL after authenticating.

        If the user has not updated their first-time information yet,
            they will be redirected to the first-time update page.

        If the user has not created a wallet yet,
            they will be redirected to the wallet creation page.

        Else, they will be redirected to home page.

        """
        updated_information = self.request.user.updated_information

        if not updated_information:
            messages.add_message(
                self.request,
                messages.INFO,
                "Please update the below information.",
            )
            return reverse_lazy(
                "first-time-update",
            )

        if not Wallet.objects.filter(
            user=self.request.user,
        ).exists():
            return reverse_lazy("wallet-create")

        return reverse_lazy("home")


class RegisterView(CreateView):
    """View for user registration."""

    form_class = UserRegistrationForm
    template_name = "users/auth/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form) -> HttpResponse:
        """Handle valid form.

        Add the message to the destination page.

        """
        response = super().form_valid(form)
        messages.add_message(
            self.request,
            messages.INFO,
            "Register successfully. Please login.",
        )
        return response


class UserFirstUpdateView(LoginRequiredMixin, UpdateView):
    """After successfully registered, user must update their information.

    Information they need to provide: first name, last name,
        default currency, and date of birth.

    After updating successfully, the user will be redirected to the
        wallet creation page.

    """

    model = User
    form_class = UserFirstUpdateForm
    template_name = "users/auth/first_update.html"
    success_url = reverse_lazy("wallet-create")

    def get_object(self, queryset=None):
        """Get the user object."""
        return self.request.user

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """If the form is valid, set the updated_information to True."""
        self.request.user.updated_information = True
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, BaseListView):
    """Provide list view page for User model.

    Users can search other users through User list page view.

    """

    model = User
    context_object_name = "users"
    template_name = "users/user_list.html"
    filter_class = UserFilter

    def get_queryset(self) -> QuerySet:
        """Get all users except the current user."""
        return super().get_queryset().exclude(pk=self.request.user.pk)


class UserDetailView(LoginRequiredMixin, DetailView):
    """Provide detail view page for User model."""

    model = User
    context_object_name = "user"
    template_name = "users/user_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Return addtional information to support Add Friend feature.

        Check the current User detail view to indicate whether it is own
        profile, has been requested to be friend or has accepted to be friend.

        """
        context = super().get_context_data(**kwargs)
        user_data = {}

        target_user = kwargs.get("object", None)
        user_data["target_user"] = target_user
        friend_request = Friendship.objects.filter(
            Q(from_user=self.request.user, to_user=target_user) |
            Q(from_user=target_user, to_user=self.request.user),
        )

        if (friend_request := friend_request.first()):
            user_data["friend_request"] = friend_request

        context.update(user_data)
        return context


class AddFriendView(LoginRequiredMixin, View):
    """Provide add friend view for Friendship model."""

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Create a Friendship instance and trigger the celery task.

        Send a friend request to target user, raise a message warning when
        users send a request to whom already a friend and raise 404 error if
        users send friend request to themselves.

        """
        user_id = kwargs.get("user_id", None)
        target_user = get_object_or_404(
            User.objects.exclude(pk=request.user.pk),
            pk=user_id,
        )

        if Friendship.objects.filter(
            Q(from_user=request.user, to_user=target_user) |
            Q(from_user=target_user, to_user=request.user),
        ).exists():
            messages.add_message(
                request,
                messages.WARNING,
                f"You have sent request to {target_user.username} already!",
            )
            return redirect(reverse("user-detail", kwargs={"pk": user_id}))

        friend_request = Friendship(
            from_user=request.user,
            to_user=target_user,
        )
        friend_request.save()
        send_friend_request_notification.delay(friend_request)
        return redirect(reverse("user-detail", kwargs={"pk": user_id}))


class AcceptFriendView(LoginRequiredMixin, View):
    """Provide accept friend view for Friendship model."""

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Handle business logic for users to accept friend requests.

        Accept a friend request from sending user, raise a message warning when
        users try to accept a request of whom already a friend and raise 404
        error if users accept a friend request that does not belong to them.

        """
        request_id = kwargs.get("request_id", None)
        friend_request = get_object_or_404(
            Friendship.objects.filter(to_user=request.user),
            pk=request_id,
        )

        if friend_request.accepted:
            messages.add_message(
                request,
                messages.WARNING,
                f"You and {friend_request.from_user.username} are friends "
                "already!",
            )
            return redirect(
                reverse(
                    "user-detail",
                    kwargs={"pk": friend_request.from_user.pk},
                ),
            )

        friend_request.accepted = True
        friend_request.save()

        return redirect(
            reverse("user-detail", kwargs={"pk": friend_request.from_user.pk}),
        )


class RemoveFriendView(LoginRequiredMixin, View):
    """Provide remove friend view for Friendship model."""

    message = """You cannot unfriend as {username} is not your friend yet!"""

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Handle business logic for users to remove a friend.

        Remove a friend from user's friend list, raise a message warning when
        users try to remove a user that has not been their friend yet and raise
        404 error when users try to remove themselves from friend list.

        """
        user_id = kwargs.get("user_id", None)
        target_user = get_object_or_404(
            User.objects.exclude(pk=request.user.pk),
            pk=user_id,
        )
        friend_request = Friendship.objects.filter(
            Q(from_user=request.user, to_user=target_user) |
            Q(from_user=target_user, to_user=request.user),
        )

        if not friend_request.exists():
            messages.add_message(
                request,
                messages.WARNING,
                self.message.format(username=target_user.username),
            )
            return redirect(reverse("user-detail", kwargs={"pk": user_id}))

        friend_request.delete()
        return redirect(reverse("user-detail", kwargs={"pk": user_id}))


class CancelFriendView(RemoveFriendView):
    """Provide cancel friend view for Friendship model."""

    message = """You haven't sent friend request to {username}!"""


class DeclineFriendView(RemoveFriendView):
    """Provide decline friend view for Friendship model."""

    message = """There is no friend request from {username} to decline!"""


class FriendListView(UserListView):
    """Provide list view page for friends in User model."""

    def get_queryset(self) -> QuerySet:
        return super(UserListView, self).get_queryset().get(
            pk=self.request.user.pk,
        ).friends.all()
