# Generated by Django 5.1.1 on 2025-02-06 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_wallet_transaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlistitem',
            name='product',
        ),
    ]
