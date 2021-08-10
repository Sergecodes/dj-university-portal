# Generated by Django 3.1.3 on 2021-07-28 02:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_auto_20210727_1325'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adphoto',
            options={'verbose_name_plural': 'Ad Photos'},
        ),
        migrations.AlterModelOptions(
            name='itemlisting',
            options={'verbose_name_plural': 'Item Listings'},
        ),
        migrations.AlterModelOptions(
            name='itemlistingphoto',
            options={'verbose_name': 'Item Listing Photo', 'verbose_name_plural': 'Item Listing Photos'},
        ),
        migrations.RemoveField(
            model_name='ad',
            name='bookmarkers',
        ),
        migrations.RemoveField(
            model_name='itemcategory',
            name='group',
        ),
        migrations.RemoveField(
            model_name='itemlisting',
            name='bookmarkers',
        ),
        migrations.AddField(
            model_name='itemcategory',
            name='parent_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='sub_categories', related_query_name='sub_category', to='marketplace.itemparentcategory'),
            preserve_default=False,
        ),
    ]