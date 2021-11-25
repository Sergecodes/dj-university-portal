# Generated by Django 3.1.3 on 2021-11-25 04:11

import core.model_fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0010_auto_20211125_0111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastpaper',
            name='file',
            field=core.model_fields.DynamicStorageFileField(blank=True, upload_to='past_papers/', validators=[django.core.validators.FileExtensionValidator(['pdf'])]),
        ),
    ]
