# Generated by Django 3.1.3 on 2021-10-09 04:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('requested_items', '0007_auto_20211008_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='requesteditem',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_requested_items', related_query_name='bookmarked_requested_item', to=settings.AUTH_USER_MODEL),
        ),
    ]