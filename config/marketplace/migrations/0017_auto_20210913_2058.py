# Generated by Django 3.1.3 on 2021-09-13 20:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0016_auto_20210913_0215'),
    ]

    operations = [
        migrations.AddField(
            model_name='adlisting',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_ad_listings', related_query_name='bookmarked_ad_listing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='itemlisting',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_item_listings', related_query_name='bookmarked_item_listing', to=settings.AUTH_USER_MODEL),
        ),
    ]
