# Generated by Django 3.1.3 on 2021-10-17 22:43

import core.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Content')),
                ('posted_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-posted_datetime'],
            },
        ),
        migrations.CreateModel(
            name='PastPaper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('O', 'Ordinary Level'), ('A', 'Advanced Level'), ('BEPC', 'BEPC'), ('PROB', 'Probatoire'), ('BAC', 'Baccalaureat'), ('BACH', "HND/Bachelor's"), ('BTS', 'BTS'), ('LIC', 'Licence'), ('MS', "Master's"), ('PhD', 'Doctorate')], max_length=5, verbose_name='Level')),
                ('type', models.CharField(choices=[('COMM', 'Commercial'), ('GEN', 'General'), ('TECH', 'Technical')], default='GEN', max_length=5, verbose_name='Speciality')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(max_length=250)),
                ('file', models.FileField(blank=True, storage=core.storage_backends.PublicMediaStorage(), upload_to='past_papers/')),
                ('posted_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('written_date', models.DateField(blank=True, null=True, verbose_name='Written date')),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2)),
                ('view_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['-posted_datetime'],
            },
        ),
        migrations.CreateModel(
            name='PastPaperPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(storage=core.storage_backends.PublicMediaStorage(), upload_to='past_paper_photos/')),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
