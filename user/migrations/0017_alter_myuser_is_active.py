# Generated by Django 5.1.1 on 2025-02-19 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_wishlistitem_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
