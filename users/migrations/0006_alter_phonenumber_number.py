# Generated by Django 3.2 on 2022-08-10 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='number',
            field=models.CharField(help_text='Enter mobile number', max_length=20, verbose_name='Phone number'),
        ),
    ]
