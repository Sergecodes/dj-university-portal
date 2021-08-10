# Generated by Django 3.1.3 on 2021-07-26 12:09

import ckeditor.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hitcount.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0007_auto_20210715_0056'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35, verbose_name='Name')),
                ('name_en', models.CharField(max_length=35, null=True, verbose_name='Name')),
                ('name_fr', models.CharField(max_length=35, null=True, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Ad Categories',
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35, verbose_name='Name')),
                ('name_en', models.CharField(max_length=35, null=True, verbose_name='Name')),
                ('name_fr', models.CharField(max_length=35, null=True, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Item Categories',
            },
        ),
        migrations.CreateModel(
            name='ItemListing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField(choices=[(datetime.timedelta(days=3), '3 days'), (datetime.timedelta(days=5), '5 days'), (datetime.timedelta(days=7), '1 week'), (datetime.timedelta(days=10), '10 days'), (datetime.timedelta(days=28), '1 month')], default=datetime.timedelta(days=5), help_text='For how long should your post be available')),
                ('title', models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, verbose_name='Title')),
                ('title_en', models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, null=True, verbose_name='Title')),
                ('title_fr', models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, null=True, verbose_name='Title')),
                ('subtitle', models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle')),
                ('subtitle_en', models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle')),
                ('subtitle_fr', models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle')),
                ('slug', models.SlugField()),
                ('slug_en', models.SlugField(null=True)),
                ('slug_fr', models.SlugField(null=True)),
                ('description', ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', verbose_name='Description')),
                ('description_en', ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', null=True, verbose_name='Description')),
                ('description_fr', ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', null=True, verbose_name='Description')),
                ('datetime_added', models.DateTimeField(auto_now_add=True, verbose_name='Date/time added')),
                ('original_language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='fr', help_text='Initial language in which post was entered in.', max_length=3, verbose_name='Initial language')),
                ('condition', models.CharField(choices=[('BN', 'Brand new'), ('U', 'Used'), ('N', 'New'), ('D', 'For parts or not working')], default='N', help_text="Select the condition of the item you're listing.", max_length=3)),
                ('condition_description', models.TextField(blank=True, help_text='Provide details about the condition of a non brand-new item, including any defects or flaws, so that buyers know exactly what to expect.', null=True, verbose_name='Condition description')),
                ('condition_description_en', models.TextField(blank=True, help_text='Provide details about the condition of a non brand-new item, including any defects or flaws, so that buyers know exactly what to expect.', null=True, verbose_name='Condition description')),
                ('condition_description_fr', models.TextField(blank=True, help_text='Provide details about the condition of a non brand-new item, including any defects or flaws, so that buyers know exactly what to expect.', null=True, verbose_name='Condition description')),
                ('price', models.CharField(help_text='Figures and spaces only, no commas or dots. <br> Enter <b>0</b> for free products or services.', max_length=15, verbose_name='Price')),
                ('bookmarkers', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookmarked_items', related_query_name='bookmarked_item', to=settings.AUTH_USER_MODEL)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='marketplace.itemcategory')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_listings', related_query_name='item_listing', to='marketplace.institution')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, hitcount.models.HitCountMixin),
        ),
        migrations.CreateModel(
            name='ItemListingPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='item photos')),
                ('item_listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', related_query_name='image', to='marketplace.itemlisting')),
            ],
        ),
        migrations.CreateModel(
            name='ItemParentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('name_en', models.CharField(max_length=30, null=True, verbose_name='Name')),
                ('name_fr', models.CharField(max_length=30, null=True, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Item Parent Categories',
            },
        ),
        migrations.RemoveField(
            model_name='category',
            name='group',
        ),
        migrations.RemoveField(
            model_name='ad',
            name='language',
        ),
        migrations.RemoveField(
            model_name='ad',
            name='number_of_bookmarks',
        ),
        migrations.AddField(
            model_name='ad',
            name='original_language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], default='fr', help_text='Initial language in which post was entered in.', max_length=3, verbose_name='Initial language'),
        ),
        migrations.AddField(
            model_name='ad',
            name='price',
            field=models.CharField(default='-', help_text='Figures and spaces only, no commas or dots. <br> Enter <b>-</b> for free products or services, or if the price is part of the description.', max_length=15, verbose_name='Price'),
        ),
        migrations.AddField(
            model_name='ad',
            name='subtitle',
            field=models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle'),
        ),
        migrations.AddField(
            model_name='ad',
            name='subtitle_en',
            field=models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle'),
        ),
        migrations.AddField(
            model_name='ad',
            name='subtitle_fr',
            field=models.CharField(blank=True, help_text='Subtitles appear in search results in list view, and can increase buyer interest by providing slightly more descriptive info.', max_length=60, null=True, verbose_name='Subtitle'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='description',
            field=ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='description_en',
            field=ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='description_fr',
            field=ckeditor.fields.RichTextField(help_text='Describe the your post and provide complete and accurate details. Use a clear and concise format.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='duration',
            field=models.DurationField(choices=[(datetime.timedelta(days=3), '3 days'), (datetime.timedelta(days=5), '5 days'), (datetime.timedelta(days=7), '1 week'), (datetime.timedelta(days=10), '10 days'), (datetime.timedelta(days=28), '1 month')], default=datetime.timedelta(days=5), help_text='For how long should your post be available'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='institution',
            field=models.ForeignKey(blank=True, help_text='Allow this empty if this ad concerns no particular institution.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ads', related_query_name='ad', to='marketplace.institution'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='title',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='title_en',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='title_fr',
            field=models.CharField(help_text='A descriptive title helps buyers find your item. <br> State exactly what your post is.', max_length=80, null=True, verbose_name='Title'),
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='ParentCategory',
        ),
        migrations.AddField(
            model_name='itemcategory',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.itemparentcategory', verbose_name='Parent category'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='category',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='marketplace.adcategory'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]