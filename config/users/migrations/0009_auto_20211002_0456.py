# Generated by Django 3.1.3 on 2021-10-02 04:56

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_user_previous_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Your username should be between 4 to 15 characters and the first 4 characters must be letters. <br> It should not contain any symbols, dashes or spaces. All other characters are allowed(letters, numbers, hyphens and underscores).', max_length=15, unique=True, validators=[users.validators.UsernameValidator()], verbose_name='Username'),
        ),
    ]
