# Generated by Django 4.1.7 on 2023-03-24 17:49

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoteapp', '0008_alter_quote_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(max_length=200), size=None),
        ),
    ]
