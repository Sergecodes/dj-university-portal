# Generated by Django 3.1.3 on 2021-10-17 22:43

import core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMediaFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', core.fields.NormalizedEmailField(blank=True, max_length=50, verbose_name='Email address')),
                ('twitter_follow', models.CharField(blank=True, max_length=50, verbose_name='Twitter link or username')),
                ('facebook_follow', models.CharField(blank=True, max_length=50, verbose_name='Facebook link or username')),
                ('instagram_follow', models.CharField(blank=True, max_length=50, verbose_name='Instagram link or username')),
                ('tiktok_follow', models.CharField(blank=True, max_length=50, verbose_name='Tiktok link or username')),
                ('github_follow', models.CharField(blank=True, max_length=50, verbose_name='GitHub link or username')),
                ('website_follow', models.CharField(blank=True, help_text='An example could be a link to a YouTube channel or Likee profile, etc.. <br> Separate multiple links with a semicolon.', max_length=250, verbose_name='Other website links')),
            ],
        ),
    ]
