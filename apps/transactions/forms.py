from decimal import Decimal
from typing import Any

from django import forms
from django.db.models import Q
from django.forms import DateInput, ModelForm, ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.rates.models import ExchangeRate
from apps.transactions.services import can_create_more_wallets
from apps.users.models import User

from .constants import NORMAL_USER_LIMITS
from .models import Category, Transaction, Wallet
from .tasks import send_shared_bill_notification


class CategoryForm(ModelForm):
    """Provide a form for Category model at create page."""

    user = None

    class Meta:
        model = Category
        fields = ["name", "is_income"]

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """Validate that the user can create a new wallet.

        Normal user can only create `max_custom_category_count` wallets.
        Premium user can create as many wallets as they want.

        """
        categories_count = Category.objects.filter(user=self.user).count()

        if (
            categories_count >= NORMAL_USER_LIMITS["max_custom_category_count"]
            and not self.user.is_premium
        ):
            raise ValidationError(
                "You cannot have more than "
                f"{NORMAL_USER_LIMITS['max_custom_category_count']} custom "
                "categories. Please upgrade to premium to unlock this feature",
            )
        return super().clean()

    def save(self, *args, **kwargs):
        """Save the form with instance user is the request user."""
        self.instance.user = self.user
        return super().save(*args, **kwargs)


class CategoryUpdateForm(ModelForm):
    """Provide a form for updating a category."""

    class Meta:
        model = Category
        fields = ["name"]


class WalletForm(ModelForm):
    """Provide a form for creating a new wallet."""

    user = None

    balance = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=0,
    )

    class Meta:
        model = Wallet
        fields = ["name", "balance", "currency", "bank"]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with the user instance.

        Pop the user instance from the kwargs and save it in the form's
        user attribute.

        """
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """Validate that the user can create a new wallet.

        Normal user can only create "max_wallets_count" wallets.
        Premium user can create as many wallets as they want.


        If there is not an exchange rate between the user's default
        currency and the chosen currency, raise a validation error.

        """
        if not can_create_more_wallets(self.user):
            raise ValidationError(
                "You can't create more wallets. Please upgrade to premium.",
            )

        user_chosen_currency = self.cleaned_data.get("currency")
        if user_chosen_currency.code != self.user.default_currency:
            exchange_rate = ExchangeRate.objects.filter(
                user=self.user,
                source_currency=user_chosen_currency,
                destination_currency__code=self.user.default_currency,
            )
            if not exchange_rate.exists():
                raise ValidationError(
                    "There is not an exchange rate between "
                    f"{user_chosen_currency} and "
                    f"{self.user.default_currency}.",
                )
        return super().clean()

    def save(self, *args, **kwargs):
        """Save the form.

        Set the wallet's owner to the current user.

        """
        self.instance.user = self.user
        return super().save(*args, **kwargs)


class WalletUpdateForm(ModelForm):
    """Provide a form for updating a wallet."""

    balance = forms.DecimalField(
        max_digits=20,
        decimal_places=3,
        min_value=0,
    )

    class Meta:
        model = Wallet
        fields = ["name", "balance", "bank"]


class TransactionForm(ModelForm):
    """Provide a form for creating a new transaction."""

    user = None
    wallet = forms.ModelChoiceField(queryset=Wallet.objects.all())
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    tagged_friends = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
    )
    date = forms.DateField(
        required=True,
        initial=timezone.now().date,
        widget=DateInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Select a date"),
                "type": "date",
            },
        ),
    )

    class Meta:
        model = Transaction
        fields = [
            "amount",
            "category",
            "wallet",
            "date",
            "note",
            "is_shared",
            "tagged_friends",
        ]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with the user instance.

        Pop the user instance from the kwargs and save it in the form's
        user attribute. Update queryset for wallet and category so that users
        can only see their properties.

        """
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["wallet"].queryset = Wallet.objects.filter(user=self.user)
        self.fields["tagged_friends"].queryset = self.user.friends.all()
        self.fields["category"].queryset = Category.objects.filter(
            Q(user=self.user) | Q(user__isnull=True),
        )

    def clean_amount(self) -> Any:
        """Ensure amount must be a positive value."""
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            self.add_error(
                "amount",
                ValidationError(_("Amount must be positive value!")),
            )

        return amount

    def clean(self) -> dict[str, Any]:
        """Check if user's wallet can handle the transaction amount.

        Ensure that if a transaction is not income type, the amount cannot be
        greater than current balance of user's chosen wallet.

        """
        amount = self.cleaned_data["amount"]
        category = self.cleaned_data["category"]
        wallet = self.cleaned_data["wallet"]
        is_shared = self.cleaned_data["is_shared"]
        tagged_friends = self.cleaned_data.get("tagged_friends", None)
        rate_obj = ExchangeRate.objects.filter(
            user=self.user,
            source_currency=wallet.currency,
            destination_currency__code=self.user.default_currency,
        ).first()

        rate = rate_obj.rate if rate_obj else Decimal(1)

        if tagged_friends and not is_shared:
            raise ValidationError(
                "Please tick Shared box if it is a Shared Bill Transaction!",
            )
        if not category.is_income and amount > wallet.balance * rate:
            raise ValidationError(
                "Transaction amount is greater than wallet's balance. "
                "Please change wallet!",
            )

        self.cleaned_data["rate"] = rate
        return super().clean()

    def save(self, *args, **kwargs):
        """Save the transaction creation form.

        Set the transaction's owner to the current user.

        """
        self.instance.user = self.user
        amount = self.cleaned_data["amount"]
        category = self.cleaned_data["category"]
        wallet = self.cleaned_data["wallet"]
        rate = self.cleaned_data["rate"]
        friends = self.cleaned_data["tagged_friends"]
        transaction = super().save(*args, **kwargs)

        if category.is_income:
            wallet.balance += amount / rate
        else:
            wallet.balance -= amount / rate

        send_shared_bill_notification.delay(self.user, friends, transaction)
        wallet.save()
        return transaction
