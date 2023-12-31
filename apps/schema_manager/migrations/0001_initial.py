# Generated by Django 4.2 on 2023-08-11 10:09

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []  # type: ignore[var-annotated]

    operations = [
        migrations.CreateModel(
            name="DynamicTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("fields", models.JSONField()),
            ],
        ),
    ]
