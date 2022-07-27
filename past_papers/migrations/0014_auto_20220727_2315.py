# Generated by Django 3.2 on 2022-07-27 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20220724_2245'),
        ('past_papers', '0013_alter_pastpaper_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pastpaper',
            name='school',
        ),
        migrations.AddField(
            model_name='pastpaper',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='past_papers', related_query_name='past_paper', to='core.country', verbose_name='Country'),
            preserve_default=False,
        ),
    ]