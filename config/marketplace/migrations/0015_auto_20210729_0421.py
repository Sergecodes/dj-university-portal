# Generated by Django 3.1.3 on 2021-07-29 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0014_auto_20210729_0411'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemcategory',
            options={'verbose_name_plural': 'Item Categories'},
        ),
        migrations.AlterModelOptions(
            name='itemsubcategory',
            options={'verbose_name_plural': 'Item Subcategories'},
        ),
    ]