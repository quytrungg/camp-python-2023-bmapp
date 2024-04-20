from django.db import migrations

from ..constants import DEFAULT_BANKS


def create_default_banks(apps, schema_editor) -> None:
    """Generate default banks for users to create linked wallets."""
    Bank = apps.get_model("transactions", "Bank")
    banks_data = [
        Bank(name=bank["name"], code=bank["code"])
        for bank in DEFAULT_BANKS
    ]

    Bank.objects.bulk_create(banks_data)


def delete_default_banks(apps, schema_editor) -> None:
    """Delete all default data in Banks when revert migration."""
    Bank = apps.get_model("transactions", "Bank")
    Bank.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('transactions', '0006_bank_code'),
    ]

    operations = [
        migrations.RunPython(
            create_default_banks,
            reverse_code=delete_default_banks,
        ),
    ]
