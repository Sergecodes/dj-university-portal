# Generated by Django 3.1.3 on 2021-09-02 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lost_and_found', '0006_auto_20210902_0200'),
    ]

    operations = [
        migrations.CreateModel(
            name='LostItemPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=60, null=True)),
                ('file', models.ImageField(upload_to='lost_items_photos/')),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
                ('lost_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', related_query_name='photo', to='lost_and_found.lostitem')),
            ],
            options={
                'verbose_name': 'Lost Items Photo',
                'verbose_name_plural': 'Lost Items Photos',
            },
        ),
    ]
