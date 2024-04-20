import factory

from apps.rates.models import Currency, ExchangeRate


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    """Provide a factory class for ExchangeRate model.

    There is no mean that users are allowed to create a new currency,
        so we don't use CurrencyFactory here.

    """

    class Meta:
        model = ExchangeRate

    user = factory.SubFactory("apps.users.factories.UserFactory")
    source_currency = factory.Iterator(Currency.objects.all())
    destination_currency = factory.Iterator(Currency.objects.all())
    rate = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )
