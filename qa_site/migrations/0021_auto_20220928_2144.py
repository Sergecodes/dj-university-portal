# Generated by Django 3.2 on 2022-09-28 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0020_auto_20220928_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicquestion',
            name='title',
            field=models.CharField(max_length=150, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='academicquestion',
            name='title_en',
            field=models.CharField(max_length=150, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='academicquestion',
            name='title_fr',
            field=models.CharField(max_length=150, null=True, verbose_name='Title'),
        ),
    ]