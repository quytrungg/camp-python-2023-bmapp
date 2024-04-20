# Generated by Django 4.2 on 2023-04-13 08:13

from django.db import migrations
from ..constants import BASIC_CURRENCIES


def add_basic_currencies(apps, schema_editor) -> None:
    """Add basic currencies to the database."""
    Currency = apps.get_model("rates", "Currency")
    currencies_to_create = [
        Currency(name=currency["name"], code=currency["code"])
        for currency in BASIC_CURRENCIES
    ]
    Currency.objects.bulk_create(currencies_to_create)


def delete_basic_currencies(apps, schema_editor) -> None:
    """Remove basic currencies from database, when undo migration."""
    Currency = apps.get_model("rates", "Currency")
    basic_currency_names = [currency['name'] for currency in BASIC_CURRENCIES]
    Currency.objects.filter(name__in=basic_currency_names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rates", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            add_basic_currencies,
            reverse_code=delete_basic_currencies,
        ),
    ]