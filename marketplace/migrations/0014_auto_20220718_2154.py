# Generated by Django 3.2 on 2022-07-18 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_auto_20220714_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlisting',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='ad_listings', related_query_name='ad_listing', to='marketplace.adcategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemcategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemsubcategory', verbose_name='Sub category'),
        ),
        migrations.AlterField(
            model_name='itemsubcategory',
            name='parent_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sub_categories', related_query_name='sub_category', to='marketplace.itemcategory'),
        ),
    ]
