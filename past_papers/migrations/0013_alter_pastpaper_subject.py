# Generated by Django 3.2 on 2022-07-18 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0008_alter_academicquestion_subject'),
        ('past_papers', '0012_auto_20220714_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastpaper',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='past_papers', related_query_name='past_paper', to='qa_site.subject', verbose_name='Subject'),
        ),
    ]
