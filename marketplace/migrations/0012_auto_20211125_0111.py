# Generated by Django 3.1.3 on 2021-11-25 01:11

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_auto_20211124_2345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adlistingphoto',
            name='height',
        ),
        migrations.RemoveField(
            model_name='adlistingphoto',
            name='width',
        ),
        migrations.RemoveField(
            model_name='itemlistingphoto',
            name='height',
        ),
        migrations.RemoveField(
            model_name='itemlistingphoto',
            name='width',
        ),
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