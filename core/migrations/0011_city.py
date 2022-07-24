# Generated by Django 3.2 on 2022-07-24 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_institution_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('datetime_added', models.DateTimeField(auto_now_add=True, verbose_name='Date/time added')),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cities', related_query_name='city', to='core.country', verbose_name='Country')),
            ],
        ),
    ]
