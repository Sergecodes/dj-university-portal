# Generated by Django 3.1.3 on 2021-08-18 01:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0007_auto_20210817_1521'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pastpaper',
            name='title_en',
        ),
        migrations.RemoveField(
            model_name='pastpaper',
            name='title_fr',
        ),
    ]
