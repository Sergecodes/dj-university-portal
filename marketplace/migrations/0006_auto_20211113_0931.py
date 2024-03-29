# Generated by Django 3.1.3 on 2021-11-13 09:31

import core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_auto_20211113_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlistingphoto',
            name='file',
            field=core.fields.DynamicStorageImageField(upload_to='ad_photos/'),
        ),
        migrations.AlterField(
            model_name='itemlistingphoto',
            name='file',
            field=core.fields.DynamicStorageImageField(upload_to='item_photos/'),
        ),
    ]
