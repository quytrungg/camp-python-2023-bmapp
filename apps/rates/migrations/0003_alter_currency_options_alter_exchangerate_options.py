# Generated by Django 4.2 on 2023-04-14 04:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rates", "0002_migrate_basic_currencies"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="currency",
            options={"verbose_name": "Currency", "verbose_name_plural": "Currencies"},
        ),
        migrations.AlterModelOptions(
            name="exchangerate",
            options={
                "verbose_name": "Exchange rate",
                "verbose_name_plural": "Exchange rates",
            },
        ),
    ]
