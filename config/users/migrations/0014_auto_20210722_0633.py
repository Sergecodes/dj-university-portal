# Generated by Django 3.1.3 on 2021-07-22 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20210722_0439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='number',
            field=models.CharField(help_text='Enter mobile number <b>(without +237)</b>', max_length=20, verbose_name='Phone number'),
        ),
    ]