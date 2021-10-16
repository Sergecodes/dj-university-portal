# Generated by Django 3.1.3 on 2021-09-10 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_auto_20210908_2129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adlisting',
            options={'ordering': ['-datetime_added']},
        ),
        migrations.AlterModelOptions(
            name='itemlisting',
            options={'ordering': ['-datetime_added'], 'verbose_name_plural': 'Item Listings'},
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='fr', help_text='Initial language in which post was entered.', max_length=3, verbose_name='Initial language'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='fr', help_text='Initial language in which post was entered.', max_length=3, verbose_name='Initial language'),
        ),
    ]