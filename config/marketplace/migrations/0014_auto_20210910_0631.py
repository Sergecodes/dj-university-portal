# Generated by Django 3.1.3 on 2021-09-10 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_auto_20210910_0345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlisting',
            name='title',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='title_en',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='title_fr',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='title',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='title_en',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='title_fr',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=100, null=True, verbose_name='Title'),
        ),
    ]