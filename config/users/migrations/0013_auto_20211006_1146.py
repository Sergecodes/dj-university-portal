# Generated by Django 3.1.3 on 2021-10-06 11:46

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20211006_0411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='full_name',
            field=models.CharField(help_text='Enter a valid full name. It should be two or three of your names separated by a spaceand each name may contain only letters or hyphens. <br>No name should start or end with a hyphen, and no name should contain only hyphens.', max_length=25, validators=[core.validators.FullNameValidator()], verbose_name='Full name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Your username should be between 4 to 15 characters and the first 4 characters must be letters. <br> It should not contain any symbols, dashes or spaces. <br>All other characters are allowed(letters, numbers, hyphens and underscores).', max_length=15, unique=True, validators=[core.validators.UsernameValidator()], verbose_name='Username'),
        ),
    ]
