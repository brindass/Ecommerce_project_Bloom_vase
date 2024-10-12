# Generated by Django 5.1.1 on 2024-09-28 01:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_rename_image_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='base_image',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='products/base'),
            preserve_default=False,
        ),
    ]