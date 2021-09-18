# Generated by Django 3.1.3 on 2021-09-17 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0011_auto_20210910_0631'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicanswer',
            name='downvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicanswer',
            name='upvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='bookmark_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='downvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='num_answers',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='num_followers',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='upvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='downvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='upvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='bookmark_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='downvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='num_answers',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='num_followers',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='upvote_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
