# Generated by Django 3.1.3 on 2021-11-24 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0008_auto_20211124_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpaperphoto',
            name='height',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastpaperphoto',
            name='width',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
