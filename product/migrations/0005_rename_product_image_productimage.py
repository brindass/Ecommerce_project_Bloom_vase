# Generated by Django 5.1.1 on 2024-09-28 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_product_reviews'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product_image',
            new_name='ProductImage',
        ),
    ]
