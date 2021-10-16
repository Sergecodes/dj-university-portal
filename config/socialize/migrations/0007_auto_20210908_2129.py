# Generated by Django 3.1.3 on 2021-09-08 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialize', '0006_auto_20210905_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediafollow',
            name='website_follow',
            field=models.CharField(blank=True, help_text='An example could be a link to a YouTube channel or Likee profile, etc.. <br> Separate multiple links with a semicolon.', max_length=250, null=True, verbose_name='Other website links'),
        ),
    ]