# Generated by Django 5.1.1 on 2024-10-22 00:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_product_soft_deleted'),
        ('user', '0006_cart_cart_item'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Cart_item',
            new_name='CartItem',
        ),
    ]
