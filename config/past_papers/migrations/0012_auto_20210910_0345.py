# Generated by Django 3.1.3 on 2021-09-10 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0011_auto_20210901_0208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-posted_datetime']},
        ),
        migrations.AlterModelOptions(
            name='pastpaper',
            options={'ordering': ['-posted_datetime']},
        ),
    ]