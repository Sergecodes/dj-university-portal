# Generated by Django 3.1.3 on 2021-10-13 18:25

import core.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lost_and_found', '0021_auto_20211009_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lostitemphoto',
            name='file',
            field=models.ImageField(storage=core.storage_backends.PublicMediaStorage(), upload_to='lost_items_photos/'),
        ),
    ]