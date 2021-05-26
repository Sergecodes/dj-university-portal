# Generated by Django 3.1.3 on 2021-02-18 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistedIP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(editable=False, unique=True, unpack_ipv4=True)),
            ],
            options={
                'verbose_name': 'Blacklisted IP',
                'verbose_name_plural': 'Blacklisted IPs',
            },
        ),
        migrations.CreateModel(
            name='BlacklistedUserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Blacklisted User Agent',
                'verbose_name_plural': 'Blacklisted User Agents',
            },
        ),
        migrations.CreateModel(
            name='HitCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_hits', models.PositiveIntegerField(default=0)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'hit count',
                'verbose_name_plural': 'hit counts',
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('ip', models.GenericIPAddressField(db_index=True, editable=False, unpack_ipv4=True)),
                ('session', models.CharField(db_index=True, editable=False, max_length=40)),
                ('user_agent', models.CharField(editable=False, max_length=255)),
                ('hitcount', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='hits', related_query_name='hit', to='hitcount.hitcount')),
            ],
            options={
                'verbose_name': 'hit',
                'verbose_name_plural': 'hits',
                'ordering': ('-created',),
                'get_latest_by': 'created',
            },
        ),
    ]
