# Generated by Django 3.1.3 on 2021-08-17 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('past_papers', '0002_auto_20210817_0116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastpaperphoto',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
