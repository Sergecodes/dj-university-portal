# Generated by Django 3.1.3 on 2021-11-24 22:55

import core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_imageholder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageholder',
            name='file',
            field=core.fields.DynamicStorageImageField(height_field='height', upload_to='temporal_photos/', width_field='width'),
        ),
    ]
