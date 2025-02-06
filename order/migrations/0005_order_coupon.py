# Generated by Django 5.1.1 on 2025-01-30 07:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_admin', '0002_rename_discount_coupon_discount_percentage'),
        ('order', '0004_returnreason'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='my_admin.coupon'),
        ),
    ]
