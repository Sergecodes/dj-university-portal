# Generated by Django 3.1.3 on 2021-11-13 07:06

import core.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requested_items', '0003_auto_20211101_0400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesteditemphoto',
            name='file',
            field=core.model_fields.DynamicStorageFileField(upload_to='requested_items_photos/'),
        ),
    ]