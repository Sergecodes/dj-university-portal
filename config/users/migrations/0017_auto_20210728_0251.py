# Generated by Django 3.1.3 on 2021-07-28 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0010_auto_20210728_0251'),
        ('users', '0016_auto_20210727_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bookmarked_ads',
            field=models.ManyToManyField(related_name='bookmarkers', related_query_name='bookmarker', to='marketplace.Ad'),
        ),
        migrations.AddField(
            model_name='user',
            name='bookmarked_listings',
            field=models.ManyToManyField(related_name='bookmarkers', related_query_name='bookmarker', to='marketplace.ItemListing'),
        ),
    ]
