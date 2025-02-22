# Generated by Django 5.1.1 on 2025-02-07 07:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_admin', '0002_rename_discount_coupon_discount_percentage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_sales_delivered', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_order_count', models.IntegerField(default=0)),
                ('coupon_discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_actual_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_offer_discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
