# Generated by Django 3.2 on 2022-09-28 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0015_pastpaper_download_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=2000, verbose_name='Content'),
        ),
    ]
