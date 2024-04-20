from django.contrib.auth import get_user_model

from apps.core.api.serializers import ModelBaseSerializer


class UserSerializer(ModelBaseSerializer):
    """Serializer for representing `User`."""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "friends",
            "avatar",
            "is_premium",
            "last_login",
            "created",
            "modified",
        )
        read_only_fields = (
            "email",
            "is_premium",
            "friends",
            "last_login",
            "created",
            "modified",
        )


class ProfileSerializer(ModelBaseSerializer):
    """Serializer for representing `Profile`."""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "phone_number",
            "date_of_birth",
            "is_active",
            "is_staff",
            "is_premium",
            "transaction_count",
            "transaction_streak",
            "updated_information",
            "default_currency",
        )
        read_only_fields = (
            "email",
            "last_login",
            "created",
            "modified",
        )


class FriendSerializer(ModelBaseSerializer):
    """Serializer for Friends API."""

    friend_list = UserSerializer(
        source="friends",
        many=True,
    )

    class Meta:
        model = get_user_model()
        fields = ("friend_list",)
        read_only_fields = ("friend_list",)
