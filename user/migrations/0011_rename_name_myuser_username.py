# Generated by Django 5.1.1 on 2024-11-25 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_delete_socialappsite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myuser',
            old_name='name',
            new_name='username',
        ),
    ]
