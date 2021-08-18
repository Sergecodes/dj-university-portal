# Generated by Django 3.1.3 on 2021-08-18 03:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialize', '0004_socialprofile_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMediaFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_follow', models.CharField(blank=True, max_length=30, null=True, verbose_name='Twitter link or username')),
                ('facebook_follow', models.CharField(blank=True, max_length=30, null=True, verbose_name='Facebook link or username')),
                ('instagram_follow', models.CharField(blank=True, max_length=30, null=True, verbose_name='Instagram link or username')),
            ],
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='social_media',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='socialize.socialmediafollow'),
        ),
    ]
