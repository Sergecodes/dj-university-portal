# Generated by Django 3.1.3 on 2021-07-31 06:32

import core.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0016_auto_20210730_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='contact_name',
            field=core.model_fields.TitleCaseField(default='new contact', help_text='Enter real names, buyers will more easily trust you if you enter a real name.', max_length=25, verbose_name='Full name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itemlisting',
            name='contact_name',
            field=core.model_fields.TitleCaseField(default='new contact', help_text='Enter real names, buyers will more easily trust you if you enter a real name.', max_length=25, verbose_name='Full name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ad',
            name='contact_email',
            field=core.model_fields.LowerCaseEmailField(help_text='Email address to use for notifications', max_length=50, verbose_name='Email address'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='contact_email',
            field=core.model_fields.LowerCaseEmailField(help_text='Email address to use for notifications', max_length=50, verbose_name='Email address'),
        ),
    ]
