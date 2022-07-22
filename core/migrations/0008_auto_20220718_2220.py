# Generated by Django 3.2 on 2022-07-18 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20220714_0425'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('datetime_added', models.DateTimeField(auto_now_add=True, verbose_name='Date/time added')),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='institution',
            name='location',
            field=models.CharField(blank=True, help_text='Street or quarter where institution is located', max_length=60, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='institution',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='institutions', related_query_name='institution', to='core.country', verbose_name='Country'),
        ),
    ]