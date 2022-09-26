# Generated by Django 3.2 on 2022-07-30 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qa_site', '0013_auto_20220726_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicquestion',
            name='subject',
            field=models.ForeignKey(blank=True, help_text="Allow this field empty if your subject is not present <br>You may add the subject's name after the question title.", null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='academic_questions', related_query_name='academic_question', to='qa_site.subject', verbose_name='Subject'),
        ),
    ]