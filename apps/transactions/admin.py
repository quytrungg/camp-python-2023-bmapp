from decimal import Decimal

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django_object_actions import (
    DjangoObjectActions,
    takes_instance_or_queryset,
)

from apps.core.admin import BaseAdmin

from .models import Bank, SharedBill, Transaction, Wallet


class SharedBillInline(admin.TabularInline):
    """Create SharedBill inline."""

    model = SharedBill
    extra = 1


@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    """Provide Admin UI for Transaction model."""

    ordering = ["date"]

    list_display = (
        "id",
        "user",
        "amount",
        "category",
        "wallet",
        "date",
        "note",
        "is_shared",
    )
    list_display_links = (
        "user",
        "amount",
        "category",
        "wallet",
        "date",
        "note",
        "is_shared",
    )
    search_fields = (
        "user",
        "amount",
        "category",
        "wallet",
        "date",
        "note",
        "is_shared",
    )
    inlines = [
        SharedBillInline,
    ]


@admin.register(Wallet)
class WalletAdmin(DjangoObjectActions, BaseAdmin):
    """Provide Admin UI for Wallet model."""

    ordering = ["name"]
    actions = ["modify_balance"]
    change_actions = ["modify_balance"]

    list_display = (
        "name",
        "user",
        "bank",
        "balance",
        "currency",
    )
    list_display_links = (
        "name",
        "bank",
        "balance",
        "currency",
    )
    search_fields = (
        "name",
        "bank",
        "balance",
        "currency",
    )

    @takes_instance_or_queryset
    def modify_balance(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ) -> HttpResponseRedirect | HttpResponse:
        """Create action to modify Wallet's balance."""

        def get_wallet_balance(request_data, wallet_pk) -> Decimal:
            """Get wallet balance from form."""
            return request_data[f"balance_modify_{wallet_pk}"]

        if "set" in request.POST:
            for wallet in queryset:
                balance = get_wallet_balance(request.POST, wallet.pk)
                wallet.set_balance(balance)

            self.message_user(
                request,
                f"Set balance successfully on {queryset.count()} Wallet(s)!",
            )

            return HttpResponseRedirect(request.get_full_path())

        if "add" in request.POST:
            for wallet in queryset:
                balance = get_wallet_balance(request.POST, wallet.pk)
                wallet.set_balance(wallet.balance + Decimal(balance))

            self.message_user(
                request,
                f"Increase balance successfully on "
                f"{queryset.count()} Wallet(s)!",
            )

            return HttpResponseRedirect(request.get_full_path())

        if "reduce" in request.POST:
            for wallet in queryset:
                balance = get_wallet_balance(request.POST, wallet.pk)
                wallet.set_balance(wallet.balance - Decimal(balance))

            self.message_user(
                request,
                f"Decrease balance successfully on "
                f"{queryset.count()} Wallet(s)!",
            )

            return HttpResponseRedirect(request.get_full_path())

        return render(
            request,
            "transactions/wallets/admin/modify_balance.html",
            context={"wallets": queryset},
        )

    modify_balance.short_description = "Modify Wallet's balance"


@admin.register(Bank)
class BankAdmin(BaseAdmin):
    """Provide Admin UI for Bank model."""

    ordering = ["name"]

    list_display = (
        "name",
        "code",
        "logo",
    )
    list_display_links = (
        "name",
    )
    search_fields = (
        "name",
    )


@admin.register(SharedBill)
class SharedBillAdmin(BaseAdmin):
    """Provide Admin UI for SharedBill model."""

    ordering = ("-id",)
    list_display = ("id", "transaction", "friend")
    list_display_links = ("id", "transaction", "friend")
    search_fields = ("id", "transaction", "friend")
