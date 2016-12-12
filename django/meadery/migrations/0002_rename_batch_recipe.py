# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-12 06:32
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meadery', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batch',
            old_name='recipe',
            new_name='batch_recipe',
        ),
        migrations.AlterField(
            model_name='batch',
            name='batchletter',
            field=models.CharField(help_text='Letter corresponding to batch (e.g., A)', max_length=1, verbose_name='Batch Letter'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='brewname',
            field=models.CharField(help_text='Unique value for brew name (e.g., SIP 99)', max_length=8, verbose_name='Brew Name'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='event',
            field=models.CharField(help_text='Brewing event (e.g., Lughnasadh 2013, Samhain 2012, Imbolc 2011, Beltane 2010)', max_length=20, verbose_name='Brewing event'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='jars',
            field=models.IntegerField(help_text='Number of jars actually produced from this batch.'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='appellation',
            field=models.CharField(help_text='Where the ingredient was made (i.e., Oregon, California, Brazil)', max_length=20, verbose_name='Appellation'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='cpu',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), help_text='Cost in USD per unit (kilogram if solid, liter if liquid, other if other)', max_digits=5, verbose_name='Cost Per Unit'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='is_natural',
            field=models.BooleanField(default=False, help_text='TRUE if the ingredient does not contain added color, artificial flavors, or synthetic substances.'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Ingredient name', max_length=40, verbose_name='Ingredient Name'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='sg',
            field=models.DecimalField(decimal_places=3, default=Decimal('1.000'), help_text='Specific gravity (water is 1.000, honey is usually 1.422)', max_digits=4, verbose_name='Specific Gravity'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='sh',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), help_text='Specific heat (water is 1.00, honey is usually 0.57)', max_digits=3, verbose_name='Specific Heat'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='state',
            field=models.IntegerField(choices=[(1, 'Solid'), (2, 'Liquid'), (3, 'Other')], default=1),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='subtype',
            field=models.IntegerField(choices=[('Sugar', ((101, 'Honey'), (102, 'Malt'), (103, 'Other'))), ('Solvent', ((201, 'Water'), (202, 'Grape Juice'), (203, 'Apple Juice'), (204, 'Fruit Juice'), (205, 'Other'))), ('Flavor', ((301, 'Spice'), (302, 'Grape'), (303, 'Apple'), (304, 'Fruit'), (305, 'Other'))), ('Yeast', ((401, 'Dry'), (402, 'Wet')))], default=101),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='tolerance',
            field=models.IntegerField(default=12, help_text='Maximum alcohol tolerance in percent (only for yeast)', verbose_name='Alcohol tolerance'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='type',
            field=models.IntegerField(choices=[(1, 'Sugar'), (2, 'Solvent'), (3, 'Flavor'), (4, 'Yeast')], default=1),
        ),
        migrations.AlterField(
            model_name='ingredientitem',
            name='amount',
            field=models.DecimalField(decimal_places=3, help_text='Amount of ingredient (kilograms if solid, liters if liquid, units if other)', max_digits=5),
        ),
        migrations.AlterField(
            model_name='ingredientitem',
            name='temp',
            field=models.IntegerField(help_text='Temperature of ingredient in degrees Fahrenheit'),
        ),
        migrations.AlterField(
            model_name='parent',
            name='category',
            field=models.IntegerField(choices=[('Traditional Mead', ((241, 'Dry Mead'), (242, 'Semi-Sweet Mead'), (243, 'Sweet Mead'))), ('Melomel', ((251, 'Cyser'), (252, 'Pyment'), (253, 'Other Fruit Melomel'))), ('Other Meads', ((261, 'Metheglin'), (262, 'Braggot'), (263, 'Open Category Mead'))), ('All Meads', ((291, 'All'),))], default=241),
        ),
        migrations.AlterField(
            model_name='parent',
            name='description',
            field=models.TextField(help_text='Description of product.'),
        ),
        migrations.AlterField(
            model_name='parent',
            name='title',
            field=models.CharField(help_text='Recipe title', max_length=40),
        ),
        migrations.AlterField(
            model_name='product',
            name='batchletter',
            field=models.CharField(help_text='Letter corresponding to batch (e.g., A)', max_length=1, verbose_name='Batch Letter'),
        ),
        migrations.AlterField(
            model_name='product',
            name='brewname',
            field=models.CharField(help_text='Unique value for brew name (e.g., SIP 99)', max_length=8, verbose_name='Brew Name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/products/main'),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_description',
            field=models.CharField(help_text='Content for description meta tag', max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_keywords',
            field=models.CharField(help_text='Comma-delimited set of SEO keywords for meta tag', max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, help_text='Unique value for product page URL, created from brewname and batchletter.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='images/products/thumbnails'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(5, '5 - Outstanding'), (4, '4 - Excellent'), (3, '3 - Very Good'), (2, '2 - Good'), (1, '1 - Fair')], default=5),
        ),
        migrations.AlterField(
            model_name='sample',
            name='notes',
            field=models.TextField(help_text='Tasting notes'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='sg',
            field=models.DecimalField(decimal_places=3, default=Decimal('0.000'), help_text='Specific gravity of mead', max_digits=4),
        ),
        migrations.AlterField(
            model_name='sample',
            name='temp',
            field=models.IntegerField(default=60, help_text='Temperature of mead in degrees Fahrenheit'),
        ),
    ]
