# Generated by Django 3.2 on 2022-07-18 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_institution_country'),
        ('users', '0003_auto_20220718_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='users', related_query_name='user', to='core.country', verbose_name='Country of residence'),
            preserve_default=False,
        ),
    ]
