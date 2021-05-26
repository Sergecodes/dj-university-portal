# Generated by Django 3.1.3 on 2021-02-18 23:43

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import core.validators
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists'}, help_text='We will send a code to this email', max_length=50, unique=True, verbose_name='Email address')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='This is the name people will know you by on this site. You can always change it later.', max_length=15, unique=True)),
                ('full_name', models.CharField(blank=True, help_text='Two of your names will be okay.', max_length=25, null=True, validators=[core.validators.validate_full_name], verbose_name='Full name')),
                ('status', models.CharField(choices=[('A', 'active'), ('D', 'deleted'), ('S', 'suspended')], default='A', max_length=2)),
                ('deletion_datetime', models.DateTimeField(blank=True, null=True)),
                ('datetime_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_mod', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Suspension',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('duration', models.DurationField(default=datetime.timedelta(days=1))),
                ('is_active', models.BooleanField(default=True)),
                ('reason', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suspensions', related_query_name='suspension', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
