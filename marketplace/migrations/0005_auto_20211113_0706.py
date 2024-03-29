# Generated by Django 3.1.3 on 2021-11-13 07:06

import core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_auto_20211103_0312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlistingphoto',
            name='file',
            field=core.fields.DynamicStorageFileField(upload_to='ad_photos/'),
        ),
        migrations.AlterField(
            model_name='itemlistingphoto',
            name='file',
            field=core.fields.DynamicStorageFileField(upload_to='item_photos/'),
        ),
    ]
