# Generated by Django 3.2 on 2022-09-27 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0014_auto_20220727_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpaper',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
