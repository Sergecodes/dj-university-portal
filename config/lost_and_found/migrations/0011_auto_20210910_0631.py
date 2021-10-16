# Generated by Django 3.1.3 on 2021-09-10 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lost_and_found', '0010_auto_20210910_0345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='founditem',
            name='area_found',
            field=models.CharField(help_text='Where did you find the item?', max_length=250),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='area_found_en',
            field=models.CharField(help_text='Where did you find the item?', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='area_found_fr',
            field=models.CharField(help_text='Where did you find the item?', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='item_found',
            field=models.CharField(help_text='What have you found?', max_length=100),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='item_found_en',
            field=models.CharField(help_text='What have you found?', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='founditem',
            name='item_found_fr',
            field=models.CharField(help_text='What have you found?', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='area_lost',
            field=models.CharField(help_text='Where do you think you lost the item?', max_length=250),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='area_lost_en',
            field=models.CharField(help_text='Where do you think you lost the item?', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='area_lost_fr',
            field=models.CharField(help_text='Where do you think you lost the item?', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_lost',
            field=models.CharField(help_text='What have you lost?', max_length=100),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_lost_en',
            field=models.CharField(help_text='What have you lost?', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lostitem',
            name='item_lost_fr',
            field=models.CharField(help_text='What have you lost?', max_length=100, null=True),
        ),
    ]