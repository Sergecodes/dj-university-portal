# Generated by Django 3.2 on 2022-07-24 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_city_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ['name'], 'verbose_name_plural': 'Cities'},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name_plural': 'Countries'},
        ),
    ]