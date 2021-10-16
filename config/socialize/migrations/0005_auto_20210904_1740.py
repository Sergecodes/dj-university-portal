# Generated by Django 3.1.3 on 2021-09-04 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialize', '0004_auto_20210904_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediafollow',
            name='website_follow',
            field=models.CharField(blank=True, help_text='An example could be a link to a YouTube channel or Likee profile, etc.. <br> Separate multiple links with a comma or semicolon.', max_length=250, null=True, verbose_name='Other website links'),
        ),
    ]