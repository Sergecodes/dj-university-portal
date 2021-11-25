# Generated by Django 3.1.3 on 2021-11-25 00:10

import core.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20211124_2345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageholder',
            name='height',
        ),
        migrations.RemoveField(
            model_name='imageholder',
            name='width',
        ),
        migrations.AlterField(
            model_name='imageholder',
            name='file',
            field=core.model_fields.DynamicStorageImageField(upload_to='temporal_photos/'),
        ),
    ]
