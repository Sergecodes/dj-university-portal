# Generated by Django 3.1.3 on 2021-10-13 18:25

import core.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0027_auto_20211008_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlistingphoto',
            name='file',
            field=models.ImageField(storage=core.storage_backends.PublicMediaStorage(), upload_to='ad_photos/'),
        ),
        migrations.AlterField(
            model_name='itemlistingphoto',
            name='file',
            field=models.ImageField(storage=core.storage_backends.PublicMediaStorage(), upload_to='item_photos/'),
        ),
    ]
