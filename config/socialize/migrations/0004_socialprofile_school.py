# Generated by Django 3.1.3 on 2021-08-18 02:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0026_auto_20210811_0028'),
        ('socialize', '0003_auto_20210818_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialprofile',
            name='school',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='social_profiles', related_query_name='social_profile', to='marketplace.institution'),
            preserve_default=False,
        ),
    ]
