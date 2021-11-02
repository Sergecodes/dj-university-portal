# Generated by Django 3.1.3 on 2021-11-01 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requested_items', '0002_auto_20211017_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description_en',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', null=True, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description_fr',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', null=True, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_requested',
            field=models.CharField(help_text='What item do you need?', max_length=100, unique=True, verbose_name='Item requested'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_requested_en',
            field=models.CharField(help_text='What item do you need?', max_length=100, null=True, unique=True, verbose_name='Item requested'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_requested_fr',
            field=models.CharField(help_text='What item do you need?', max_length=100, null=True, unique=True, verbose_name='Item requested'),
        ),
    ]