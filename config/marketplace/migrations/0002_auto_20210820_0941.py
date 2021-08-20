# Generated by Django 3.1.3 on 2021-08-20 09:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemlisting',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_listings', related_query_name='item_listing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='itemlisting',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemsubcategory'),
        ),
        migrations.AddField(
            model_name='adlistingphoto',
            name='ad_listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', related_query_name='photo', to='marketplace.adlisting'),
        ),
        migrations.AddField(
            model_name='adlisting',
            name='category',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='marketplace.adcategory'),
        ),
        migrations.AddField(
            model_name='adlisting',
            name='institution',
            field=models.ForeignKey(blank=True, help_text='Allow this empty if this ad concerns no particular institution.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ads', related_query_name='ad', to='marketplace.institution'),
        ),
        migrations.AddField(
            model_name='adlisting',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ad_listings', related_query_name='ad_listing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='itemlisting',
            index=models.Index(fields=['-datetime_added'], name='marketplace_datetim_e4838d_idx'),
        ),
        migrations.AddIndex(
            model_name='adlisting',
            index=models.Index(fields=['-datetime_added'], name='marketplace_datetim_5cd968_idx'),
        ),
    ]
