from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import DateInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.rates.models import Currency
from apps.users.models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""

    email = forms.EmailField(
        max_length=254,
        help_text=_("Enter your email address"),
    )

    phone_number = forms.CharField(
        max_length=15,
        help_text=_("Enter your phone number"),
        validators=[
            RegexValidator(
                regex=r"^\+84[0-9]{9}$",
            ),
        ],
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number",
            "password1",
            "password2",
        )


class UserFirstUpdateForm(forms.ModelForm):
    """Form for handle the information update for the first time."""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text=_("Enter your first name"),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text=_("Enter your last name"),
    )

    date_of_birth = forms.DateField(
        required=True,
        help_text=_("Enter your date of birth"),
        widget=DateInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Select a date"),
                "type": "date",
            },
        ),
    )

    default_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        help_text=_("Select your default currency"),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "default_currency",
        )

    def clean_date_of_birth(self):
        """Ensure that date of birth is not in the future."""
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date_of_birth and date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
        return date_of_birth
