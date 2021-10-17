# Generated by Django 3.1.3 on 2021-10-17 22:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lost_and_found', '0001_initial'),
        ('users', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lostitem',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_lost_items', related_query_name='bookmarked_lost_item', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lostitem',
            name='contact_numbers',
            field=models.ManyToManyField(related_name='_lostitem_contact_numbers_+', to='users.PhoneNumber', verbose_name='Contact numbers'),
        ),
        migrations.AddField(
            model_name='lostitem',
            name='poster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lost_items', related_query_name='lost_item', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lostitem',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lost_items', related_query_name='lost_item', to='core.institution'),
        ),
        migrations.AddField(
            model_name='founditem',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_found_items', related_query_name='bookmarked_found_item', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='founditem',
            name='contact_numbers',
            field=models.ManyToManyField(related_name='_founditem_contact_numbers_+', to='users.PhoneNumber', verbose_name='Contact numbers'),
        ),
        migrations.AddField(
            model_name='founditem',
            name='poster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='found_items', related_query_name='found_item', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='founditem',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='found_items', related_query_name='found_item', to='core.institution', verbose_name='School'),
        ),
        migrations.AddIndex(
            model_name='lostitem',
            index=models.Index(fields=['-posted_datetime'], name='lost_and_fo_posted__ae3e94_idx'),
        ),
        migrations.AddIndex(
            model_name='founditem',
            index=models.Index(fields=['-posted_datetime'], name='lost_and_fo_posted__5efadc_idx'),
        ),
    ]
