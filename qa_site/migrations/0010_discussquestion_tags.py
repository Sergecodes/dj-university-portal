# Generated by Django 3.2 on 2022-07-25 11:39

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0009_auto_20220725_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussquestion',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='qa_site.TaggedDiscussQuestion', to='qa_site.DiscussQuestionTag', verbose_name='Tags'),
        ),
    ]
