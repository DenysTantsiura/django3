# Generated by Django 4.1.7 on 2023-03-26 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoteapp', '0013_alter_quote_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='born_location',
            field=models.CharField(max_length=60),
        ),
    ]
