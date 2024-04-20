from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from imagekit.admin import AdminThumbnail

from apps.rates.models import ExchangeRate
from apps.transactions.models import Category

from ..core.admin import BaseAdmin
from .models import Friendship, User


class CategoryInline(admin.TabularInline):
    """Category inline."""

    model = Category
    extra = 1


class ExchangeRateInline(admin.TabularInline):
    """Exchange rate inline."""

    model = ExchangeRate
    extra = 1


@admin.register(User)
class UserAdmin(BaseAdmin, DjangoUserAdmin):
    """UI for User model."""

    ordering = ("email",)
    avatar_thumbnail = AdminThumbnail(image_field="avatar_thumbnail")
    list_display = (
        "username",
        "avatar_thumbnail",
        "phone_number",
        "email",
        "is_premium",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )
    list_display_links = (
        "username",
    )
    search_fields = (
        "username",
        "phone_number",
        "first_name",
        "last_name",
        "email",
    )
    add_fieldsets = (
        (
            None, {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    fieldsets = (
        (
            None, {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            _("Personal info"), {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "phone_number",
                ),
            },
        ),
        (
            _("Permissions"), {
                "fields": (
                    "is_premium",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    inlines = [
        ExchangeRateInline,
        CategoryInline,
    ]


@admin.register(Friendship)
class FriendRequestAdmin(BaseAdmin):
    """Provide Admin UI for Friendship model."""

    ordering = ("-id",)
    list_display = ("id", "from_user", "to_user", "accepted")
    list_display_links = ("id", "from_user", "to_user", "accepted")
    search_fields = ("id", "from_user", "to_user", "accepted")
