# Generated by Django 3.1.3 on 2021-08-12 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0006_auto_20210811_2338'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolQuestionTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('name_en', models.CharField(max_length=30, null=True, unique=True)),
                ('name_fr', models.CharField(max_length=30, null=True, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='slug_en',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='slug_fr',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='title',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='title_en',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='title_fr',
        ),
        migrations.RemoveField(
            model_name='schoolquestion',
            name='tags',
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='tags',
            field=models.ManyToManyField(related_name='school_questions', related_query_name='school_question', to='qa_site.SchoolQuestionTag'),
        ),
    ]
