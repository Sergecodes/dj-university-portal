# Generated by Django 3.1.3 on 2021-08-14 18:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qa_site', '0009_auto_20210812_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicanswer',
            name='downvoters',
            field=models.ManyToManyField(blank=True, related_name='downvoted_academic_answers', related_query_name='downvoted_academic_answer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='academicanswer',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_academic_answers', related_query_name='upvoted_academic_answer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='downvoters',
            field=models.ManyToManyField(blank=True, related_name='downvoted_academic_questions', related_query_name='downvoted_academic_question', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_academic_questions', related_query_name='upvoted_academic_question', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='downvoters',
            field=models.ManyToManyField(blank=True, related_name='downvoted_school_answers', related_query_name='downvoted_school_answer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_school_answers', related_query_name='upvoted_school_answer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='downvoters',
            field=models.ManyToManyField(blank=True, related_name='downvoted_school_questions', related_query_name='downvoted_school_question', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_school_questions', related_query_name='upvoted_school_question', to=settings.AUTH_USER_MODEL),
        ),
    ]
