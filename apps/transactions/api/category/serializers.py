from apps.core.api.serializers import ModelBaseSerializer
from apps.core.exceptions import NonFieldValidationError
from apps.transactions.api.transactions.serializers import (
    TransactionSerializer,
)
from apps.transactions.models import Category
from apps.transactions.services import can_create_more_category


class CategoryListSerializer(ModelBaseSerializer):
    """Serializer for Category list API."""

    def create(self, validated_data):
        """Create new category for authenticated user.

        Raise NonFieldValidationError if user can't create more categories,
        e.g. they are not premium and they already have reached the limit of
        categories.

        Add authenticated user to the validated data.

        """
        if not can_create_more_category(self.context["request"].user):
            raise NonFieldValidationError(
                "You can't create more categories. Please upgrade to premium.",
            )

        validated_data["user"] = self.context["request"].user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update category.

        Do not allow user to modify system category
        or to modify user and is_income fields.

        """
        if instance.user is None:
            raise NonFieldValidationError(
                "Not allowed to modify system category.",
            )

        validated_data.pop("is_income", None)

        return super().update(instance, validated_data)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "is_income",
            "user",
        )
        read_only_fields = (
            "id",
            "user",
        )


class CategoryDetailSerializer(CategoryListSerializer):
    """Serializer for Category detail API.

    Add 'transactions' field to the response.

    """

    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta(CategoryListSerializer.Meta):
        """Add transactions field to the detail API's response."""

        fields = CategoryListSerializer.Meta.fields + ("transactions",)
