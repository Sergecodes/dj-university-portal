# Generated by Django 3.1.3 on 2021-09-29 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210927_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='follow_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]