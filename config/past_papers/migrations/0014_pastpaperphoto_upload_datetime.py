# Generated by Django 3.1.3 on 2021-09-12 18:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0013_auto_20210912_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpaperphoto',
            name='upload_datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]