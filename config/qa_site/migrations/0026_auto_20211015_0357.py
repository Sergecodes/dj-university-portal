# Generated by Django 3.1.3 on 2021-10-15 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0025_taggedacademicquestion_content_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicanswer',
            name='update_language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2),
        ),
        migrations.AddField(
            model_name='academicquestion',
            name='update_language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2),
        ),
        migrations.AddField(
            model_name='schoolanswer',
            name='update_language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2),
        ),
        migrations.AddField(
            model_name='schoolquestion',
            name='update_language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, max_length=2),
        ),
    ]