# Generated by Django 3.1.3 on 2021-11-13 09:31

import core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requested_items', '0004_auto_20211113_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesteditemphoto',
            name='file',
            field=core.fields.DynamicStorageImageField(upload_to='requested_items_photos/'),
        ),
    ]
