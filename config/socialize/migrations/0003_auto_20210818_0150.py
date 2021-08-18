# Generated by Django 3.1.3 on 2021-08-18 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialize', '0002_auto_20210818_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialprofile',
            name='about_me_en',
            field=models.TextField(null=True, verbose_name='A little about me'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='about_me_fr',
            field=models.TextField(null=True, verbose_name='A little about me'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='hobbies_en',
            field=models.TextField(null=True, verbose_name='My hobbies'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='hobbies_fr',
            field=models.TextField(null=True, verbose_name='My hobbies'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='interests_en',
            field=models.TextField(null=True, verbose_name='My interests'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='interests_fr',
            field=models.TextField(null=True, verbose_name='My interests'),
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='level',
            field=models.CharField(choices=[('L1', 'Level 1'), ('L2', 'Level 2'), ('L3', 'Level 3'), ('L4', 'Level 5'), ('M', 'Masters'), ('PhD', 'Doctorate'), ('Other', 'Other')], default='L1', max_length=7),
            preserve_default=False,
        ),
    ]
