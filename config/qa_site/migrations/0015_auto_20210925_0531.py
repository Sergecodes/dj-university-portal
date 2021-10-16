# Generated by Django 3.1.3 on 2021-09-25 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0014_auto_20210918_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicanswer',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='academicanswercomment',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='academicquestioncomment',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='schoolanswercomment',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='schoolquestioncomment',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='schoolquestiontag',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]