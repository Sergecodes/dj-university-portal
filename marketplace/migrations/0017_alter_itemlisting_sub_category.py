# Generated by Django 3.2 on 2022-07-24 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0016_auto_20220724_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemlisting',
            name='sub_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemsubcategory', verbose_name='Sub category'),
            preserve_default=False,
        ),
    ]
