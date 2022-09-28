# Generated by Django 3.2 on 2022-09-28 20:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qa_site', '0018_auto_20220928_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussCommentUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upvote_datetime', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='qa_site.discusscomment')),
                ('upvoter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AcademicCommentUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upvote_datetime', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='qa_site.academiccomment')),
                ('upvoter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AcademicCommentDownvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('downvote_datetime', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='qa_site.academiccomment')),
                ('downvoter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='academiccomment',
            name='downvoters',
            field=models.ManyToManyField(blank=True, related_name='downvoted_academic_comments', related_query_name='downvoted_academic_comment', through='qa_site.AcademicCommentDownvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='academiccomment',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_academic_comments', related_query_name='upvoted_academic_comment', through='qa_site.AcademicCommentUpvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discusscomment',
            name='upvoters',
            field=models.ManyToManyField(blank=True, related_name='upvoted_discuss_comments', related_query_name='upvoted_discuss_comment', through='qa_site.DiscussCommentUpvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='discusscommentupvote',
            constraint=models.UniqueConstraint(fields=('comment', 'upvoter'), name='unique_discuss_comment_upvote'),
        ),
        migrations.AddConstraint(
            model_name='academiccommentupvote',
            constraint=models.UniqueConstraint(fields=('comment', 'upvoter'), name='unique_academic_comment_upvote'),
        ),
        migrations.AddConstraint(
            model_name='academiccommentdownvote',
            constraint=models.UniqueConstraint(fields=('comment', 'downvoter'), name='unique_academic_comment_downvote'),
        ),
    ]
