# Generated by Django 3.1.3 on 2021-07-14 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_auto_20210322_0314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='condition_description',
            field=models.TextField(help_text='Provide details about the condition of a non brand new item, including any defects or flaws, so that buyers know exactly what to expect.', verbose_name='Condition description'),
        ),
        migrations.AlterField(
            model_name='item',
            name='condition_description_en',
            field=models.TextField(help_text='Provide details about the condition of a non brand new item, including any defects or flaws, so that buyers know exactly what to expect.', null=True, verbose_name='Condition description'),
        ),
        migrations.AlterField(
            model_name='item',
            name='condition_description_fr',
            field=models.TextField(help_text='Provide details about the condition of a non brand new item, including any defects or flaws, so that buyers know exactly what to expect.', null=True, verbose_name='Condition description'),
        ),
    ]
