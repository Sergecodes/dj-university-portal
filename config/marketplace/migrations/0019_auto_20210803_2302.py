# Generated by Django 3.1.3 on 2021-08-03 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0018_auto_20210801_0300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemlistingphoto',
            name='item_listing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='images', related_query_name='image', to='marketplace.itemlisting'),
            preserve_default=False,
        ),
    ]
