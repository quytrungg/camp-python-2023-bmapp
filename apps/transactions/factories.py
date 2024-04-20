import factory

from apps.rates.models import Currency

from .models import Category, Transaction, Wallet


class CategoryFactory(factory.django.DjangoModelFactory):
    """Provide a factory class for Category model."""

    class Meta:
        model = Category

    name = factory.Faker("word")
    is_income = factory.Faker("pybool")


class TransactionFactory(factory.django.DjangoModelFactory):
    """Provide a factory class for Transaction model."""

    class Meta:
        model = Transaction

    note = factory.Faker("sentence")
    is_shared = factory.Faker("pybool")
    date = factory.Faker("date")
    category = factory.SubFactory(
        "apps.transactions.factories.CategoryFactory",
    )
    amount = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )


class WalletFactory(factory.django.DjangoModelFactory):
    """Factory for Wallet model."""

    class Meta:
        model = Wallet

    name = factory.Faker("word")
    user = factory.SubFactory("apps.users.factories.UserFactory")
    currency = factory.Iterator(Currency.objects.all())
    bank = None
    balance = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )
