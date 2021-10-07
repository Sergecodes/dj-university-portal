# Generated by Django 3.1.3 on 2021-10-07 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_institution'),
        ('users', '0014_auto_20211007_0128'),
        ('marketplace', '0025_auto_20211002_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adlisting',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ad_listings', related_query_name='ad_listing', to='marketplace.adcategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='contact_numbers',
            field=models.ManyToManyField(related_name='_adlisting_contact_numbers_+', to='users.PhoneNumber', verbose_name='Contact numbers'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='pricing',
            field=models.CharField(default='-', help_text='Allow this field empty for free products and services or if the pricing is in the advert description.', max_length=40, verbose_name='Pricing'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='pricing_en',
            field=models.CharField(default='-', help_text='Allow this field empty for free products and services or if the pricing is in the advert description.', max_length=40, null=True, verbose_name='Pricing'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='pricing_fr',
            field=models.CharField(default='-', help_text='Allow this field empty for free products and services or if the pricing is in the advert description.', max_length=40, null=True, verbose_name='Pricing'),
        ),
        migrations.AlterField(
            model_name='adlisting',
            name='school',
            field=models.ForeignKey(blank=True, help_text='Allow this field empty if this advert does not concern a particular school.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_listings', related_query_name='ad_listing', to='core.institution', verbose_name='School'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemcategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='condition',
            field=models.CharField(choices=[('N', 'New'), ('U', 'Used'), ('D', 'Defective(some parts are not working)')], default='N', help_text="Select the condition of the item you're listing.", max_length=3, verbose_name='Condition'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='contact_numbers',
            field=models.ManyToManyField(related_name='_itemlisting_contact_numbers_+', to='users.PhoneNumber', verbose_name='Contact numbers'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_listings', related_query_name='item_listing', to='core.institution', verbose_name='School'),
        ),
        migrations.AlterField(
            model_name='itemlisting',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_listings', related_query_name='item_listing', to='marketplace.itemsubcategory', verbose_name='Sub category'),
        ),
    ]
