# Generated by Django 3.1.3 on 2021-11-13 09:31

import core.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lost_or_found', '0003_auto_20211113_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lostitemphoto',
            name='file',
            field=core.model_fields.DynamicStorageImageField(upload_to='lost_items_photos/'),
        ),
    ]