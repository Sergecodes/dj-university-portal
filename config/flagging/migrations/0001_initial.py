# Generated by Django 3.1.3 on 2021-10-17 22:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('state', models.SmallIntegerField(choices=[(1, 'Unflagged'), (2, 'Flagged'), (3, 'Flag rejected by the moderator'), (5, 'Content modified by the author'), (4, 'Creator notified')], default=1)),
                ('count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Flag',
            },
        ),
        migrations.CreateModel(
            name='FlagInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_flagged', models.DateTimeField(auto_now_add=True)),
                ('reason', models.SmallIntegerField(choices=[(1, 'Spam | Exists only to promote a service '), (2, 'Abusive | Intended at promoting hatred'), (100, 'Something else')], default=1)),
                ('info', models.TextField(blank=True, null=True)),
                ('flag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flags', to='flagging.flag')),
            ],
            options={
                'verbose_name': 'Flag Instance',
                'verbose_name_plural': 'Flag Instances',
                'ordering': ['-date_flagged'],
            },
        ),
    ]
