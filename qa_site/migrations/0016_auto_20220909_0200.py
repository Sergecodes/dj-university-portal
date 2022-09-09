# Generated by Django 3.2 on 2022-09-09 02:00

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qa_site', '0015_discusscomment_users_mentioned'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('original_language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2)),
                ('update_language', models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2)),
                ('content', ckeditor.fields.RichTextField(verbose_name='Content')),
                ('content_en', ckeditor.fields.RichTextField(null=True, verbose_name='Content')),
                ('content_fr', ckeditor.fields.RichTextField(null=True, verbose_name='Content')),
                ('downvoters', models.ManyToManyField(blank=True, related_name='downvoted_academic_comments', related_query_name='downvoted_academic_comment', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', related_query_name='reply', to='qa_site.academiccomment')),
                ('poster', models.ForeignKey(on_delete=models.SET(users.models.get_dummy_user), related_name='academic_comments', related_query_name='academic_comment', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', related_query_name='comment', to='qa_site.academicquestion')),
                ('upvoters', models.ManyToManyField(blank=True, related_name='upvoted_academic_comments', related_query_name='upvoted_academic_comment', to=settings.AUTH_USER_MODEL)),
                ('users_mentioned', models.ManyToManyField(blank=True, related_name='academic_comments_mentioned', related_query_name='academic_comment_mentioned', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Academic Comment',
                'verbose_name_plural': 'Academic Comments',
            },
        ),
        migrations.RemoveField(
            model_name='academicanswercomment',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='academicanswercomment',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='academicanswercomment',
            name='poster',
        ),
        migrations.RemoveField(
            model_name='academicanswercomment',
            name='upvoters',
        ),
        migrations.RemoveField(
            model_name='academicanswercomment',
            name='users_mentioned',
        ),
        migrations.RemoveField(
            model_name='academicquestioncomment',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='academicquestioncomment',
            name='poster',
        ),
        migrations.RemoveField(
            model_name='academicquestioncomment',
            name='question',
        ),
        migrations.RemoveField(
            model_name='academicquestioncomment',
            name='upvoters',
        ),
        migrations.RemoveField(
            model_name='academicquestioncomment',
            name='users_mentioned',
        ),
        migrations.DeleteModel(
            name='AcademicAnswer',
        ),
        migrations.DeleteModel(
            name='AcademicAnswerComment',
        ),
        migrations.DeleteModel(
            name='AcademicQuestionComment',
        ),
    ]
