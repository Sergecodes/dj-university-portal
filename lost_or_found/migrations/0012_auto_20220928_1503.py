# Generated by Django 3.2 on 2022-09-28 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lost_or_found', '0011_auto_20220928_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='founditem',
            name='how_found',
            field=models.TextField(help_text='Explain how you found the item', max_length=3000, verbose_name='How found'),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='how_found_en',
            field=models.TextField(help_text='Explain how you found the item', max_length=3000, null=True, verbose_name='How found'),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='how_found_fr',
            field=models.TextField(help_text='Explain how you found the item', max_length=3000, null=True, verbose_name='How found'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='how_lost',
            field=models.TextField(default='Good day, ', help_text='Explain how you think you lost the item, stating areas you passed across or visited', max_length=3000, verbose_name='How lost'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='how_lost_en',
            field=models.TextField(default='Good day, ', help_text='Explain how you think you lost the item, stating areas you passed across or visited', max_length=3000, null=True, verbose_name='How lost'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='how_lost_fr',
            field=models.TextField(default='Good day, ', help_text='Explain how you think you lost the item, stating areas you passed across or visited', max_length=3000, null=True, verbose_name='How lost'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_description',
            field=models.TextField(help_text='Describe the lost item stating its important aspects.', max_length=3000, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_description_en',
            field=models.TextField(help_text='Describe the lost item stating its important aspects.', max_length=3000, null=True, verbose_name='Item description'),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_description_fr',
            field=models.TextField(help_text='Describe the lost item stating its important aspects.', max_length=3000, null=True, verbose_name='Item description'),
        ),
    ]
