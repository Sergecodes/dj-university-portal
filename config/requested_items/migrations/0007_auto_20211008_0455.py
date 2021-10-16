# Generated by Django 3.1.3 on 2021-10-08 04:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_institution'),
        ('requested_items', '0006_auto_20211007_0128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requesteditem',
            name='contact_name',
        ),
        migrations.AlterField(
            model_name='requesteditem',
            name='school',
            field=models.ForeignKey(blank=True, help_text='Allow this field empty if you are willing to go to another area to buy the item, not in your school.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requested_items', related_query_name='requested_item', to='core.institution', verbose_name='School'),
        ),
    ]