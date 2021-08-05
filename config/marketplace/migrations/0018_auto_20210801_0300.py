# Generated by Django 3.1.3 on 2021-08-01 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0017_auto_20210731_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemlisting',
            name='condition',
            field=models.CharField(choices=[('N', 'New'), ('U', 'Used'), ('D', 'For parts or not working')], default='N', help_text="Select the condition of the item you're listing.", max_length=3),
        ),
    ]
