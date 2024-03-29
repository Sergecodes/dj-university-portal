# Generated by Django 3.1.3 on 2021-11-14 09:01

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_auto_20211113_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlistingphoto',
            name='file',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to='ad_photos/'),
        ),
        migrations.AlterField(
            model_name='itemlistingphoto',
            name='file',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to='item_photos/'),
        ),
    ]
