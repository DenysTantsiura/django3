# Generated by Django 4.1.7 on 2023-03-24 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quoteapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='quoteapp.author'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='quote',
            field=models.CharField(max_length=2000, unique=True),
        ),
    ]