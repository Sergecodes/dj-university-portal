# Generated by Django 3.1.3 on 2021-10-17 22:43

import core.model_fields
import core.storage_backends
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RequestedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('slug', models.SlugField(max_length=255)),
                ('slug_en', models.SlugField(max_length=255, null=True)),
                ('slug_fr', models.SlugField(max_length=255, null=True)),
                ('posted_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('original_language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], editable=False, help_text='Language in which post was created', max_length=2)),
                ('update_language', models.CharField(blank=True, choices=[('en', 'English'), ('fr', 'French')], editable=False, help_text='Language in which last update was done', max_length=2)),
                ('contact_email', core.model_fields.NormalizedEmailField(help_text='Email address to contact; enter a valid email.', max_length=50, validators=[django.core.validators.EmailValidator()], verbose_name='Email address')),
                ('item_requested', models.CharField(help_text='What item do you need?', max_length=100, verbose_name='Item requested')),
                ('item_requested_en', models.CharField(help_text='What item do you need?', max_length=100, null=True, verbose_name='Item requested')),
                ('item_requested_fr', models.CharField(help_text='What item do you need?', max_length=100, null=True, verbose_name='Item requested')),
                ('item_description', models.TextField(help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', verbose_name='Item description')),
                ('item_description_en', models.TextField(help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', null=True, verbose_name='Item description')),
                ('item_description_fr', models.TextField(help_text='Describe the item you are in need of, stating its important aspects. <br>You may allow this field empty.', null=True, verbose_name='Item description')),
                ('price_at_hand', models.CharField(default='-', help_text='How much are you willing to pay for the item? You may allow this field empty.', max_length=20, verbose_name='Price at hand')),
                ('price_at_hand_en', models.CharField(default='-', help_text='How much are you willing to pay for the item? You may allow this field empty.', max_length=20, null=True, verbose_name='Price at hand')),
                ('price_at_hand_fr', models.CharField(default='-', help_text='How much are you willing to pay for the item? You may allow this field empty.', max_length=20, null=True, verbose_name='Price at hand')),
            ],
            options={
                'ordering': ['-posted_datetime'],
            },
        ),
        migrations.CreateModel(
            name='RequestedItemPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(storage=core.storage_backends.PublicMediaStorage(), upload_to='requested_items_photos/')),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
                ('requested_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', related_query_name='photo', to='requested_items.requesteditem')),
            ],
            options={
                'verbose_name': 'Requested Item Photo',
                'verbose_name_plural': 'Requested Items Photos',
            },
        ),
    ]
