# Generated by Django 3.1.3 on 2021-10-07 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_institution'),
        ('qa_site', '0024_auto_20211007_0128'),
        ('past_papers', '0016_auto_20211002_1828'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pastpaper',
            old_name='default_language',
            new_name='language',
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='level',
            field=models.CharField(choices=[('O', 'Ordinary Level'), ('A', 'Advanced Level'), ('BEPC', 'BEPC'), ('PROB', 'Probatoire'), ('BAC', 'Baccalaureat'), ('BACH', "HND/Bachelor's"), ('BTS', 'BTS'), ('LIC', 'Licence'), ('MS', "Master's"), ('PhD', 'Doctorate')], max_length=5, verbose_name='Level'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='past_papers', related_query_name='past_paper', to='core.institution', verbose_name='School'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='past_papers', related_query_name='past_paper', to='qa_site.subject', verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='type',
            field=models.CharField(choices=[('COMM', 'Commercial'), ('GEN', 'General'), ('TECH', 'Technical')], default='GEN', max_length=5, verbose_name='Speciality'),
        ),
        migrations.AlterField(
            model_name='pastpaper',
            name='written_date',
            field=models.DateField(blank=True, null=True, verbose_name='Written date'),
        ),
    ]