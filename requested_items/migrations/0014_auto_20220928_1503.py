# Generated by Django 3.2 on 2022-09-28 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requested_items', '0013_auto_20220928_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', max_length=3000, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description_en',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', max_length=3000, null=True, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='item_description_fr',
            field=models.TextField(blank=True, help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', max_length=3000, null=True, verbose_name='Item description'),
        ),
    ]
