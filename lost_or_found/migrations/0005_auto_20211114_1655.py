# Generated by Django 3.1.3 on 2021-11-14 16:55

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lost_or_found', '0004_auto_20211113_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lostitemphoto',
            name='file',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to='lost_items_photos/'),
        ),
    ]
