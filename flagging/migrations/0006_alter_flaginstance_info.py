# Generated by Django 3.2 on 2022-09-28 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flagging', '0005_alter_flaginstance_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flaginstance',
            name='info',
            field=models.TextField(blank=True, max_length=3000),
        ),
    ]
