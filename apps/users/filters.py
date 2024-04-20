import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    """Provide filtering options for User model."""

    username = django_filters.CharFilter(
        lookup_expr="istartswith",
        field_name="username",
    )
    phone_number = django_filters.CharFilter(
        lookup_expr="istartswith",
        field_name="phone_number",
    )

    class Meta:
        model = User
        fields = ["username", "phone_number"]
