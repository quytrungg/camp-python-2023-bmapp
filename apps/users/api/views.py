from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.api.views import ReadOnlyViewSet
from apps.users.models import User

from . import serializers


class UsersViewSet(ReadOnlyViewSet):
    """ViewSet for viewing accounts."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = (
        "first_name",
        "last_name",
    )
    ordering_fields = (
        "first_name",
        "last_name",
    )

    @action(methods=["get"], detail=False)
    def friends(self, request: Request) -> Response:
        """Get user's list of friends."""
        serializer = serializers.FriendSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileApiView(GenericAPIView):
    """ApiView for viewing user's profile."""

    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Get user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
