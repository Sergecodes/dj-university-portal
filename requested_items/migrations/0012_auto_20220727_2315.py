# Generated by Django 3.2 on 2022-07-27 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20220724_2245'),
        ('requested_items', '0011_alter_requesteditem_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requesteditem',
            name='school',
        ),
        migrations.AddField(
            model_name='requesteditem',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='requested_items', related_query_name='requested_item', to='core.city', verbose_name='City of residence'),
            preserve_default=False,
        ),
    ]